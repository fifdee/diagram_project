from django.urls import path

from activity_colors.views import ActivityColorsUpdate

urlpatterns = [
    path('edit/', ActivityColorsUpdate.as_view(), name='activity-colors-update')
]