from django.urls import path

from apps.musorka import views

app_name = 'musorka'

urlpatterns = [
    path('musorki/', views.MusorkaListView.as_view(), name='musorki'),
    path('musorka/create/', views.CreateMusorka.as_view(), name='create'),
    path('musorka/empty/<int:pk>/', views.Empty.as_view(), name='empty'),
    path('musorka/full/<int:pk>/', views.Full.as_view(), name='full'),
    path('musorka/statistic/', views.MusorkaStatistic.as_view(), name='statistic'),
]