from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# from django.contrib.auth import User ## NOT RECOMMENDED
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def login_view(request):
    if(request.method == "POST"):
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None
        if all([username,password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next") or "/"
                if not next_url.startswith("/"):
                    next_url = "/"
                return redirect(next_url)
    return render(request, "auth/login.html", {})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or None
        email = request.POST.get("email") or None
        password = request.POST.get("password") or None
        if all([username, email, password]):
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    next_url = request.GET.get("next") or "/"
                    if not next_url.startswith("/"):
                        next_url = "/"
                    return redirect(next_url)
            except Exception as e:
                print("Registration error:", e)
    return render(request, "auth/register.html", {})