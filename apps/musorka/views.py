from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView
from django.views.generic.base import View, TemplateView

from apps.musorka.forms import CreateMusorkaForm
from apps.musorka.models import Musorka, MusorkaHistoryModel
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
        user = self.request.user
        musorka.user.add(user)
        musorka.save()
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


class MusorkaStatistic(TemplateView):
    template_name = 'musorka/statistic.html'


    def get_context_data(self, **kwargs):
        musorka = get_object_or_404(Musorka, pk=self.kwargs['pk'])

        month_count = self.__get_stat_per_month(musorka)

        context = super().get_context_data(**kwargs)

        context.update({
            'month': month_count,
        })
        return context

    def __get_stat_per_month(self, musorka):
        qs = MusorkaHistoryModel.objects.filter(musorka=musorka, full_time__month=12)
        return qs.last().counter - qs.first().counter

    def get_stats(self):
        return AbstractRequestExportStatistics.get_table_content()







