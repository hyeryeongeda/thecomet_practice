from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Follow, UserSetting
from .serializers import (
    SignupSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    ThemeSerializer,
    FollowToggleResultSerializer,
)

User = get_user_model()


def _issue_tokens(user: User):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    return Response(
        {"message": "회원가입 성공", "user": UserSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    print("LOGIN raw data:", request.data)
    print("LOGIN keys:", list(request.data.keys()))

    # ✅ 프론트에서 username/email 중 뭐가 와도 처리
    identifier = (request.data.get("username") or request.data.get("email") or "").strip()
    password = request.data.get("password", "")

    if not identifier or not password:
        return Response({"detail": "username(email)과 password는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 1) username으로 먼저 시도
    user = authenticate(request, username=identifier, password=password)

    # 2) 실패하면 email로 유저 찾고 username으로 authenticate
    if not user:
        u = User.objects.filter(email__iexact=identifier).first()
        if u:
            user = authenticate(request, username=u.username, password=password)

    if not user:
        return Response({"detail": "아이디(또는 이메일) / 비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"user": UserSerializer(user).data, "tokens": _issue_tokens(user)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


# backend/accounts/views.py

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    
    # 1. 비밀번호 변경 로직 (입력값이 있을 때만 실행)
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    
    if old_password and new_password:
        if not user.check_password(old_password):
            return Response({"detail": "현재 비밀번호가 일치하지 않습니다."}, status=400)
        user.set_password(new_password)
        user.save()
        # 비밀번호 변경 후 세션/토큰 유지를 위해 필요한 경우 처리 (SimpleJWT는 재로그인 필요 없음)

    # 2. 프로필 정보 및 이미지 업데이트
    # partial=True를 주어 일부 필드만 넘어와도 허용합니다.
    serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(user).data)
    
    return Response(serializer.errors, status=400)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_theme(request):
    setting, _ = UserSetting.objects.get_or_create(user=request.user)
    serializer = ThemeSerializer(setting, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"theme": setting.theme}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def user_profile(request, username):
    target = User.objects.filter(username=username).first()
    if not target:
        return Response({"detail": "유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    data = UserSerializer(target).data

    # ✅ 로그인 상태면 내가 팔로우 중인지 추가 제공
    is_following = False
    if getattr(request.user, "is_authenticated", False):
        is_following = Follow.objects.filter(from_user=request.user, to_user=target).exists()

    data["is_following"] = is_following
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_toggle(request, username):
    if request.user.username == username:
        return Response({"detail": "자기 자신은 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    target = User.objects.filter(username=username).first()
    if not target:
        return Response({"detail": "유저를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    rel = Follow.objects.filter(from_user=request.user, to_user=target).first()
    if rel:
        rel.delete()
        is_following = False
    else:
        Follow.objects.create(from_user=request.user, to_user=target)
        is_following = True

    result = {
        "is_following": is_following,
        "followers_count": Follow.objects.filter(to_user=target).count(),
        "following_count": Follow.objects.filter(from_user=target).count(),
    }
    return Response(FollowToggleResultSerializer(result).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def social_login_placeholder(request, provider):
    allowed = ["google", "kakao", "apple", "x", "line"]
    if provider not in allowed:
        return Response({"detail": "지원하지 않는 provider입니다."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"detail": f"{provider} 소셜 로그인은 다음 단계에서 실제 연동 로직을 붙입니다."},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )
