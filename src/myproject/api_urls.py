from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from subscriptions.api_views import SubscriptionPlansListView, CurrentUserDashboardAPIView

urlpatterns = [
    # Auth token endpoint
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Subscriptions public endpoint
    path('subscriptions/plans/', SubscriptionPlansListView.as_view(), name='api_subscriptions_plans'),
    
    # Me endpoint (profile + subscription details)
    path('me/', CurrentUserDashboardAPIView.as_view(), name='api_me'),
]
