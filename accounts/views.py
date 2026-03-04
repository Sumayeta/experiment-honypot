from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request, 'accounts/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'accounts/home.html')

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Count
from django.utils.timezone import now, timedelta
from .models import LoginSecurityLog

@login_required
def home(request):
    token_address = "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    user_ip = request.META.get("REMOTE_ADDR")

    honeypot_result = check_honeypot_is(token_address)
    honeydb_result = check_honeydb(user_ip)
    abuseipdb_result = check_abuseipdb(user_ip)
    context = {
        "honeypot": honeypot_result,
        "honeydb": honeydb_result,
        "abuse": abuseipdb_result,
    }

    return render(request, "accounts/home.html", context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def check_honeypot_is(token_address):
    try:
        response = requests.get(
            settings.HONEYPOT_IS_URL,
            params={"address": token_address},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# LOGIN
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome {user.username}")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})
# LOGOUT
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect("login")

def check_honeydb(ip_address):
    headers = {
        "Authorization": f"Bearer {settings.HONEYDB_API_KEY}"
    }

    try:
        response = requests.get(
            settings.HONEYDB_URL,
            headers=headers,
            params={"ip": ip_address},
            timeout=5
        )

        if response.status_code != 200:
            return {"status": "unavailable"}

        if not response.text.strip():
            return {"status": "no_data"}

        return response.json()

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def check_abuseipdb(ip):
    headers = {
        "Key": settings.ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 30
    }

    try:
        r = requests.get(settings.ABUSEIPDB_URL, headers=headers, params=params, timeout=5)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
    

def security_dashboard(request):
    # Last 7 days
    last_week = now() - timedelta(days=7)

    logs = LoginSecurityLog.objects.filter(created_at__gte=last_week)

    # Risk distribution
    low = logs.filter(risk_score__lt=30).count()
    medium = logs.filter(risk_score__gte=30, risk_score__lt=70).count()
    high = logs.filter(risk_score__gte=70).count()

    # Daily count
    daily_logs = (
        logs.extra(select={'day': "date(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    context = {
        "low": low,
        "medium": medium,
        "high": high,
        "daily_logs": list(daily_logs),
    }

    return render(request, "accounts/dashboard.html", context)
@login_required
def dashboard_view(request):
    # example context
    context = {
        'low': 10,
        'medium': 5,
        'high': 2,
        'daily_logs': [
            {'day': 'Mon', 'count': 5},
            {'day': 'Tue', 'count': 8},
            {'day': 'Wed', 'count': 2},
        ],
    }
    return render(request, 'accounts/dashboard.html', context)