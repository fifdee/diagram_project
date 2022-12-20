from django.urls import path

from diagram.views import ShowDiagram, SoldierList, SoldierUpdate, SoldierDetail, SoldierCreate, SoldierDelete, \
    ActivityUpdate, ActivityDelete, ActivityCreate, SoldierInfoUpdate, SoldierInfoNamesUpdate, SoldierInfoAdd, \
    SoldierInfoDelete

urlpatterns = [
    path('', ShowDiagram.as_view(), name='show-diagram'),
    path('soldier-list/', SoldierList.as_view(), name='soldier-list'),
    path('soldier-detail/<int:pk>/', SoldierDetail.as_view(), name='soldier-detail'),
    path('soldier-update/<int:pk>/', SoldierUpdate.as_view(), name='soldier-update'),
    path('soldier-create/', SoldierCreate.as_view(), name='soldier-create'),
    path('soldier-delete/<int:pk>/', SoldierDelete.as_view(), name='soldier-delete'),
    path('activity-create/<int:soldier_pk>/', ActivityCreate.as_view(), name='activity-create'),
    path('activity-update/<int:pk>/', ActivityUpdate.as_view(), name='activity-update'),
    path('activity-delete/<int:pk>/', ActivityDelete.as_view(), name='activity-delete'),
    path('soldier-info-update/<int:soldier_pk>/', SoldierInfoUpdate.as_view(), name='soldier-info-update'),
    path('soldier-info-names-update/<int:soldier_pk>/', SoldierInfoNamesUpdate.as_view(),
         name='soldier-info-names-update'),
    path('soldier-info-add/<int:soldier_pk>/', SoldierInfoAdd.as_view(), name='soldier-info-add'),
    path('soldier-info-delete/<int:pk>/', SoldierInfoDelete.as_view(), name='soldier-info-delete'),
]
