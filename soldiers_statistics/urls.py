from django.urls import path

from soldiers_statistics.views import StatisticsView

urlpatterns = [
    path('', StatisticsView.as_view(), name='statistics'),
]