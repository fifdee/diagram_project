from django.urls import path

from diagram.views import ShowDiagram, SoldierList, SoldierUpdate, SoldierDetail, SoldierCreate

urlpatterns = [
    path('', ShowDiagram.as_view(), name='show-diagram'),
    path('soldier-list/', SoldierList.as_view(), name='soldier-list'),
    path('soldier-detail/<int:pk>/', SoldierDetail.as_view(), name='soldier-detail'),
    path('soldier-update/<int:pk>/', SoldierUpdate.as_view(), name='soldier-update'),
    path('soldier-create/', SoldierCreate.as_view(), name='soldier-create'),
]