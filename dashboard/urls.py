from django.urls import path

from .views import DashboardStatsView


urlpatterns = [
    path("dashboard/stats/", DashboardStatsView.as_view()),
]
