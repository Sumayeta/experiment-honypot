import requests
from django.conf import settings
from django.contrib import messages
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import LoginSecurityLog
from django.contrib.auth import logout
from django.shortcuts import redirect

def check_ip_risk(ip):
    headers = {
        "Key": settings.ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 30
    }

    try:
        r = requests.get(
            settings.ABUSEIPDB_URL,
            headers=headers,
            params=params,
            timeout=5
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}
    

@receiver(user_logged_in)
def login_security_check(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR")

    # TEMP test IP (for localhost testing)
    if ip == "127.0.0.1":
        ip = "185.220.101.1"

    result = check_ip_risk(ip)

    try:
        score = result["data"]["abuseConfidenceScore"]

        if score >= 80:
            logout(request)   # 🔥 SERVER SIDE LOGOUT (NO CSRF)
            messages.error(
                request,
                "🚫 Login blocked due to high security risk."
            )

    except Exception:
        pass

LoginSecurityLog.objects.create(
    user=user,
    ip_address=ip,
    risk_score=score
)