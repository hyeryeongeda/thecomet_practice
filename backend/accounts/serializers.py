from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserSetting, Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "birth_date",
            "gender",
            "profile_image",
            "followers_count",
            "following_count",
            "theme",
        ]

    def get_followers_count(self, obj):
        # obj를 팔로우하는 사람 수
        return Follow.objects.filter(to_user=obj).count()

    def get_following_count(self, obj):
        # obj가 팔로우하는 사람 수
        return Follow.objects.filter(from_user=obj).count()

    def get_theme(self, obj):
        if hasattr(obj, "setting") and obj.setting:
            return obj.setting.theme
        return "white"


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "password2", "name", "email", "birth_date", "gender"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        if not attrs.get("birth_date"):
            raise serializers.ValidationError("생년월일은 필수입니다.")
        g = attrs.get("gender")
        if g and g not in ["M", "F"]:
            raise serializers.ValidationError("성별 값이 올바르지 않습니다.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)  # ✅ 해시 저장
        user.save()

        UserSetting.objects.get_or_create(user=user)
        return user




from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    마이페이지 '프로필 수정'용
    - username은 보통 변경 금지(서비스 정책)
    - name/email/birth_date/gender/profile_image 정도만 수정 허용
    """
    class Meta:
        model = User
        # 수정을 허용할 필드만 나열 (username은 제외)
        fields = ["profile_image", "name", "email", "birth_date", "gender", "profile_image"]

    def validate_gender(self, value):
        # gender를 null/blank 허용이면 None/""도 허용
        if value in [None, ""]:
            return value
        if value not in ["M", "F"]:
            raise serializers.ValidationError("성별 값이 올바르지 않습니다.")
        return value


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ["theme"]


class FollowToggleResultSerializer(serializers.Serializer):
    is_following = serializers.BooleanField()
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()

