from rest_framework import serializers
from .models import Customer
import math

class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        income = validated_data['monthly_income']
        limit = int(round((36 * income) / 100000.0)) * 100000  # Round to nearest lakh
        validated_data['approved_limit'] = limit
        return Customer.objects.create(**validated_data)
