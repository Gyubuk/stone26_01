from django.urls import path
from . import views

urlpatterns = [
    path("round/<int:round_no>/", views.round_view, name="round"),
    path("result/<int:decision_id>/", views.result_view, name="result"),
    path("done/", views.done_view, name="done"),
]
