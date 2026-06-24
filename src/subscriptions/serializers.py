from rest_framework import serializers
from .models import Subscription, SubscriptionPrice, UserSubscription

class SubscriptionPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPrice
        fields = ['id', 'interval', 'price']

class SubscriptionSerializer(serializers.ModelSerializer):
    prices = SubscriptionPriceSerializer(source='subscriptionprice_set', many=True, read_only=True)
    features_list = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'name', 'subtitle', 'features_list', 'prices']

    def get_features_list(self, obj):
        return obj.get_features_as_list()

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='subscription.name', read_only=True)
    features = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'plan_name', 
            'active', 
            'status', 
            'current_period_start', 
            'current_period_end', 
            'charge_at', 
            'features'
        ]

    def get_features(self, obj):
        if obj.subscription:
            return obj.subscription.get_features_as_list()
        return []
