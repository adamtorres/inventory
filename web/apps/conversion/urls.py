from django import urls

from . import views as c_views


app_name = "conversion"

urlpatterns = [
    urls.path("", c_views.ConversionReportView.as_view(), name="average_report"),
    urls.path("measures/", c_views.MeasureListView.as_view(), name="measure_list"),
    urls.path("measure/<uuid:pk>", c_views.MeasureDetailView.as_view(), name="measure_detail"),
    urls.path("measure/new", c_views.MeasureCreateView.as_view(), name="measure_create"),
]
