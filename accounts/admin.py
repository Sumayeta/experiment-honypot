from django.contrib import admin
from .models import LoginSecurityLog

@admin.register(LoginSecurityLog)
class LoginSecurityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "risk_score", "created_at")
    list_filter = ("risk_score", "created_at")
    search_fields = ("user__username", "ip_address")