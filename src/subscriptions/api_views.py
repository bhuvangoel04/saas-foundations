from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Subscription, UserSubscription
from .serializers import SubscriptionSerializer, UserSubscriptionSerializer
from profiles.serializers import UserProfileSerializer

class SubscriptionPlansListView(ListAPIView):
    queryset = Subscription.objects.filter(active=True)
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]

class CurrentUserDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_sub, created = UserSubscription.objects.get_or_create(user=user)
        
        user_data = UserProfileSerializer(user).data
        sub_data = UserSubscriptionSerializer(user_sub).data
        
        return Response({
            "user": user_data,
            "subscription": sub_data
        })

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
