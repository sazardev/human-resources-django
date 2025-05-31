from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
import secrets
from .models import User, UserSession, LoginAttempt


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Mínimo 8 caracteres, debe incluir letras y números"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con este email."
            )
        return value.lower()

    def validate_username(self, value):
        """Validate username is unique"""
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError(
                "Este nombre de usuario ya está en uso."
            )
        return value.lower()

    def validate(self, attrs):
        """Validate password confirmation"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs

    def create(self, validated_data):
        """Create new user"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        
        # Generate email verification token
        user.email_verification_token = secrets.token_urlsafe(32)
        
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        """Authenticate user"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        request = self.context.get('request')
        
        if email and password:
            # Get IP and User Agent for logging
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Try to authenticate
            user = authenticate(
                request=request,
                username=email,
                password=password
            )
            
            # Log the attempt
            LoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=user is not None,
                failure_reason='' if user else 'Credenciales inválidas'
            )
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        'Esta cuenta está desactivada.'
                    )
                
                # Update last login IP
                user.last_login_ip = ip_address
                user.save(update_fields=['last_login_ip'])
                
                attrs['user'] = user
            else:
                raise serializers.ValidationError(
                    'Email o contraseña incorrectos.'
                )
        else:
            raise serializers.ValidationError(
                'Debe proporcionar email y contraseña.'
            )
        
        return attrs
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'profile_picture', 'date_of_birth', 'bio',
            'employee_id', 'hire_date', 'department', 'position',
            'is_email_verified', 'date_joined', 'last_login',
            'full_name'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'is_email_verified', 
            'date_joined', 'last_login'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    current_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contraseña actual es incorrecta.'
            )
        return value

    def validate(self, attrs):
        """Validate new password confirmation"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas nuevas no coinciden.'
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate email exists"""
        try:
            user = User.objects.get(email=value.lower())
            return value.lower()
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No existe una cuenta con este email."
            )


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        """Validate token and password"""
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # Find user by token
        try:
            user = User.objects.get(password_reset_token=token)
            if not user.is_password_reset_token_valid():
                raise serializers.ValidationError({
                    'token': 'El token ha expirado.'
                })
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'token': 'Token inválido.'
            })
        
        # Validate password confirmation
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden.'
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user sessions
    """
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user_email', 'ip_address', 'user_agent',
            'created_at', 'last_activity', 'is_active'
        ]


class LoginAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for login attempts
    """
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'success', 
            'attempted_at', 'failure_reason'
        ]
