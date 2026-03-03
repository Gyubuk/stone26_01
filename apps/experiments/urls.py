# apps/experiments/urls.py

from django.urls import path
from . import views

app_name = 'experiments'

urlpatterns = [
    path("round/<int:exp_no>/<int:round_no>/", views.round_view, name="round"),
    path("make_choice/", views.make_choice, name="make_choice"),
    path("result/<int:decision_id>/", views.result_view, name="result"),
    path("done/", views.done_view, name="done"),

    # 연습라운드
    path("practice/",                           views.practice_round_view, {"round_no": 1}, name="practice_round_start"),
    path("practice/<int:round_no>/",            views.practice_round_view, name="practice_round"),
    path("practice/choice/",                    views.practice_choice,     name="practice_choice"),
    path("practice/result/",                    views.practice_result_view,name="practice_result"),
]