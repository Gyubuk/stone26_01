from django.contrib import admin
from .models import Participant

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'gender', 'age', 'risk', 'lottery', 'exp', 'created_at']
    list_filter = ['gender', 'risk', 'lottery', 'exp', 'created_at']
    search_fields = ['code', 'phone', 'product']
    readonly_fields = ['code', 'created_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'consent', 'created_at')
        }),
        ('개인정보', {
            'fields': ('gender', 'age', 'phone')
        }),
        ('상품 정보', {
            'fields': ('product',)
        }),
        ('성향 측정', {
            'fields': ('risk', 'lottery', 'exp')
        }),
    )