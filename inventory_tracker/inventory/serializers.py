from rest_framework import serializers
from .models import Product, User, AppSetting



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['owner', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ['id', 'key', 'value', 'updated_by', 'updated_at']
        read_only_fields = ['updated_by', 'updated_at']