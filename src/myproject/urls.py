"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from auth import views as auth_views
from subscriptions import views as subscription_views
from .views import (
    home_page_view, 
    pw_protected_view,
    user_only_view,
    about_view,
    staff_only_view,
    )

urlpatterns = [
    path("",home_page_view, name="home"), #index page -> root page
    path("login/", auth_views.login_view),
    path("register/", auth_views.register_view),
    path("working/",home_page_view),
    path("about/",about_view),
    path("protected/",pw_protected_view),
    path("protected/user_only/",user_only_view),
    path("protected/staff_only/",staff_only_view),
    path('accounts/', include('allauth.urls')), 
    path('profiles/', include('profiles.urls')), # loads all urls from profiles app 
    path("admin/", admin.site.urls),
    path("pricing/",subscription_views.subscription_price_view, name="pricing"),
]
