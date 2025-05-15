from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from io import BytesIO

# User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "name", "birthday", "gender",
            "city", "district", "ward", "street", "company", "position",
            "university", "major", "phone", "facebook", "bio", "joined_date", "avatar"
        ]
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True},
        }

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type':'password'},
        label='Confirm Password'
    )
    class Meta:
        model = User
        fields = ['email', 'name', 'password' ,'password2']
        extra_kwargs = {
            'password':{'write_only': True, 'style':{'input_type':'password'}}
        }
    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )

        initials = validated_data['name'][:2].upper()
        avatar_file = self.create_avatar_image(initials)
        user.avatar.save(f"{initials}.png", avatar_file)
        return user


    def create_avatar_image(self, initials):
        # Tạo ảnh từ chữ cái đầu (ví dụ: "JD")
        img = Image.new('RGB', (100, 100), color='blue')
        d = ImageDraw.Draw(img)

        # Đường dẫn font hoặc font mặc định
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        d.text((25, 30), initials, fill=(255, 255, 255), font=font)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return ContentFile(buffer.getvalue(), 'avatar.png')

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type':'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()  # Blacklist the token
        except TokenError as e:
            raise serializers.ValidationError({'refresh': 'Token is invalid or already blacklisted'})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, write_only=True, style={'input-type':'password'})

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password':'Mật khẩu cũ không đúng'})
        
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password':'Mật khẩu mới không trùng khớp'})
        
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password':'Mật khẩu mới phải khác mật khẩu cũ'})

        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user    
    