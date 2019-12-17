from datetime import datetime

from django.db.models import Min, Max, Avg
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, FormView
from django.views.generic.base import View, TemplateView

from apps.musorka.forms import CreateMusorkaForm, MusorkaStatisticForm
from apps.musorka.models import Musorka, MusorkaHistoryModel
# from apps.musorka.statistic import AbstractRequestExportStatistics
from apps.musorka.statistic import AbstractRequestExportStatistics


class MusorkaListView(ListView):
    model = Musorka
    template_name = 'musorka/my_musorka.html'
    context_object_name = 'musorki'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)


class CreateMusorka(CreateView):
    model = Musorka
    form_class = CreateMusorkaForm
    template_name = 'musorka/create_musorka.html'
    success_url = reverse_lazy('musorka:musorki')

    def form_valid(self, form):
        musorka = form.save(commit=False)
        musorka.save()
        musorka.user.add(self.request.user)
        MusorkaHistoryModel.objects.create(musorka=musorka, empty_time=timezone.now())
        return super().form_valid(form)


class Full(View):

    def post(self, request, *args, **kwargs):
        musorka = get_object_or_404(Musorka, pk=kwargs['pk'])
        musorka.status = Musorka.FULL
        musorka.counter += 1
        musorka.save()
        MusorkaHistoryModel.objects.create(musorka=musorka, full_time=timezone.now(), status=Musorka.FULL, counter=musorka.counter)
        return redirect(reverse('musorka:musorki'))


class Empty(View):

    def post(self, request, *args, **kwargs):
        musorka = get_object_or_404(Musorka, pk=self.kwargs['pk'])
        musorka.status = Musorka.EMPTY
        musorka.save()
        MusorkaHistoryModel.objects.create(musorka=musorka, empty_time=timezone.now(), status=Musorka.EMPTY, counter=musorka.counter)
        return redirect(reverse('musorka:musorki'))


class MusorkaStatistic(FormView):
    form_class = MusorkaStatisticForm
    template_name = 'musorka/statistic.html'


    def get_context_data(self, **kwargs):

        month_count, cont = self.__get_stat_per_month()

        context = super().get_context_data(**kwargs)

        context.update({
            'mon': month_count,
            'cont': cont,
        })
        return context

    def __get_stat_per_month(self):
        date = datetime.strptime(self.request.GET.get('date'), '%d-%m-%Y')
        AbstractRequestExportStatistics(date)
        qs = MusorkaHistoryModel.objects.filter(full_time__lte=date).aggregate(Min('counter'), Max('counter'), Avg('counter'))
        return qs, Musorka.objects.filter(created__lte=date)








