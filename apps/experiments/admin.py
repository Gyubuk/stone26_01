from django.contrib import admin
from .models import RoundDecision

@admin.register(RoundDecision)
class RoundDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "participant", "round_no", "decision_type", "bid_value", "outcome", "paid_price", "created_at")
    list_filter = ("decision_type", "outcome", "round_no")
