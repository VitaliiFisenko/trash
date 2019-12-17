import csv
import os
import string

import time
from datetime import datetime

import xlsxwriter
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Subquery, F, Max, Q

from apps.user_profile.models import State
from apps.musorka.models import Musorka, MusorkaHistoryModel



class StatisticsRequestsCore:
    """
    Class with core filters for statistics
    by country and department/region
    """

    def __init__(self, obj):
        """
        Overwritten method to add attributes to object

        :param obj:
        """
        self.obj = obj

        self.req_model = ContentType.objects.get(model=obj.doc_request_type).model_class()
        self.date_from = datetime.combine(obj.date_from, datetime.min.time())
        self.date_to = datetime.combine(obj.date_to, datetime.max.time())
        self.no_citizenship = State.objects.get(name='Особа без громадянства')
        self.department = self.obj.department if self.obj.department else ''

    def filter_by_country(self, qs, country=None):
        """
        Method to filter request by country

        :param qs: prepared request Queryset
        :param country: State object
        :return: int
        """

        if country:
            if country == self.no_citizenship:
                count = qs.annotate(
                    latest=Max('res_person__poly_citizenship')
                ).filter(
                    (
                        Q(
                            res_person__poly_citizenship__state=country,
                            res_person__poly_citizenship__id=F('latest')) |
                        Q(
                            res_person__poly_citizenship__isnull=True)
                    ),
                    dmsudep_add__code__startswith=self.department
                ).count()
            else:
                count = qs.annotate(
                    latest=Max('res_person__poly_citizenship')
                ).filter(
                    dmsudep_add__code__startswith=self.department,
                    res_person__poly_citizenship__state=country,
                    res_person__poly_citizenship__id=F('latest'),
                ).count()
        else:
            count = qs.filter(dmsudep_add__code__startswith=self.department).count()

        return count

    def filter_by_dep(self, qs, dep_code=None, issue=False):
        """
        Method to filter request by department

        :param qs: prepared request Queryset
        :param dep_code: Department's code str
        :param issue: bool
        :return: int
        """
        if dep_code:
            if issue:
                count = qs.annotate(
                    latest=Max('requested_document')
                ).filter(
                    requested_document__dep_add__code__startswith=dep_code[:2],
                    requested_document__id=F('latest')
                ).count()

            else:
                count = qs.filter(dmsudep_add__code__startswith=dep_code[:2]).count()
        else:
            count = qs.count()

        return count

    def _get_requests_by_statuses(self, status):
        """
        Method to get counter for requests by statuses

        :param status: RequestFigurationStatus object
        :return: filtered request Queryset
        """

        subquery = MusorkaHistoryModel.objects.filter(
            created__lte=self.date_to,
            created__gte=self.date_from,
            content_type=ContentType.objects.get_for_model(self.req_model)
        ).order_by(
            'content_type', 'object_id', '-created'
        ).distinct(
            'content_type', 'object_id'
        ).values_list(
            'pk', flat=True)

        return self.req_model.objects.filter(
            request_status_history__status=status,
            request_status_history__id__in=Subquery(subquery)
        )


class AbstractRequestExportStatistics(StatisticsRequestsCore):
    """
    Abstract class to build statistics files for requests
    """

    def __init__(self, obj):
        """
        Overwritten method to add attributes to object

        :param obj:
        """
        super().__init__(obj)

        self.states = State.objects.all()

        self.csv_path = f'statistics/csv/{obj.doc_request_type}_{int(time.time())}_{obj.date_from}_{obj.date_to}.csv'
        self.xls_path = f'statistics/xls/{obj.doc_request_type}_{int(time.time())}_{obj.date_from}_{obj.date_to}.xls'

    def get_header_cells(self) -> list:
        """
        Method to get header cells

        :return:
        """
        raise NotImplementedError

    def get_row(self, row_criterion=None) -> list:
        """
        Method to get row depends on row_criterion

        :return:
        """

        raise NotImplementedError

    def _get_first_column(self):
        """
        Method to get first column with countries or regions criterion

        :return:
        """
        first_row_by_type = {
            self.obj.BY_COUNTRIES: self.states.exclude(pk=self.no_citizenship.id),
            self.obj.BY_REGION: State.REGIONS_DEP
        }

        return first_row_by_type[self.obj.statistics_type]

    def get_table_content(self):
        """
        Method to get table matrix

        :return:
        """

        content = [self.get_header_cells(), self.get_row()]

        if self.obj.statistics_type == self.obj.BY_COUNTRIES:
            content.append(self.get_row(self.states.get(pk=self.no_citizenship.id)))

        for first_column_cell in self._get_first_column():
            content.append(self.get_row(first_column_cell))
        return content

    def create_csv(self, data):
        """
        Method to save data as csv file

        :param data:
        :return:
        """
        with open(os.path.join(settings.MEDIA_ROOT, self.csv_path), 'w+', encoding='utf-8') as f:
            file_csv = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for doc_req in data:
                file_csv.writerow(doc_req)

        return self.csv_path

    def create_xls(self, data):
        """
        Method to save data as xls file

        :param data:
        :return:
        """

        raise NotImplementedError

    def save_statistics(self):
        """
        Method to generate and save statistics files

        :return:
        """

        os.makedirs(os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.csv_path)), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, os.path.dirname(self.xls_path)), exist_ok=True)

        data = self.get_table_content()

        csv_file = self.create_csv(data)
        xls_file = self.create_xls(data)

        return csv_file, xls_file


class ExcelFile(xlsxwriter.Workbook):
    """
    Class inherited from Workbook with additional methods
    """

    base_format_dict = {'bold': 1, 'border': 1, 'align': 'left', 'valign': 'vcenter'}

    def __init__(self, xls_file_path):
        """
        Overwritten method to add file path

        :param xls_file_path:
        """
        super().__init__(os.path.join(settings.MEDIA_ROOT, xls_file_path))
        self.xls_file_path = xls_file_path

    def _base_format(self):
        """
        Method to get base format

        :return:
        """
        base_format = self.add_format(self.base_format_dict)
        base_format.set_text_wrap()
        return base_format

    def content_format(self):
        """
        Method to get format for table content

        :return:
        """
        return self._base_format()

    def title_format(self):
        """
        Method to get format for title content

        :return:
        """
        title_format = self._base_format()
        title_format.set_align('center')
        return title_format

    def header_format(self):
        """
        Method to set format for header content

        :return:
        """
        header_format = self._base_format()
        header_format.set_align('center')
        header_format.set_fg_color('#B3B3B3')
        return header_format

    def color_format(self, color):
        """
        Method to get format with color

        :param color:
        :return:
        """
        color_format = self.add_format({'bg_color': color})
        return color_format

    @staticmethod
    def get_column_label_by_index(index):
        """
        Method to get column label by index

        :param index:
        :return:
        """
        alphabet_len = len(string.ascii_uppercase)

        if index >= alphabet_len:
            label = f'A{string.ascii_uppercase[index - alphabet_len]}'
        else:
            label = string.ascii_uppercase[index]

        return label
