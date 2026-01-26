from django.urls import path
from . import views
app_name = 'experiments'

urlpatterns = [
    path("round/<int:round_number>/", views.round_view, name="round"),
    path('make_choice/', views.make_choice, name='make_choice'),
    path('result/<int:decision_id>/', views.result_view, name='result'),
    path("done/", views.done_view, name="done"),
]
