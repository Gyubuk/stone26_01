from django.urls import path
from . import views

app_name = 'participants'

urlpatterns = [
    path("trait/", views.trait, name="trait"),
]