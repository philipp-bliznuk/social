import clearbit
from pyhunter import PyHunter
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(required=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'password')

    def validate_email(self, value):
        hunter = PyHunter(settings.HUNTER_API_KEY)
        if not (settings.HUNTER_ENABLED and settings.HUNTER_API_KEY) or \
                        hunter.email_verifier(value).get('result') != 'undeliverable':
            return value
        raise serializers.ValidationError('Email address doesn\'t look real')

    def create(self, validated_data):
        email = validated_data.get('email')
        user = User.objects.create_user(
            email, validated_data.get('full_name'), validated_data.get('password')
        )
        if settings.CLEARBIT_ENABLED and settings.CLEARBIT_API_KEY:
            clearbit.key = settings.CLEARBIT_API_KEY
            response = clearbit.Enrichment.find(email=email, stream=True)
            if response:
                user.person = response['person']
                user.company = response['company']
                user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'author', 'title', 'text', 'created_at')
