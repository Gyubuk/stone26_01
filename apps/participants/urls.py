from django.urls import path
from . import views

urlpatterns = [
    path("trait/", views.trait, name="trait"),
]