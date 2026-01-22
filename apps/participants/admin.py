from django.contrib import admin
from .models import Participant

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "consent", "risk", "loss", "exp", "created_at")
    list_filter = ("consent", "risk", "loss", "exp")
