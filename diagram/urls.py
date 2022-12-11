from django.urls import path

from diagram.views import ShowDiagram

urlpatterns = [
    path('', ShowDiagram.as_view(), name='show-diagram'),
]