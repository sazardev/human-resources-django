from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import secrets

from .models import User, UserSession, LoginAttempt
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSessionSerializer,
    LoginAttemptSerializer
)
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            # TODO: Send verification email
            # self.send_verification_email(user)
            
            return Response({
                'message': 'Usuario creado exitosamente',
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        """Send email verification"""
        # TODO: Implement email verification
        pass


class UserLoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)
              # Create or get authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            # Create user session
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Deactivate old sessions if not remember_me
            if not remember_me:
                # Finalizar sesiones anteriores
                old_sessions = UserSession.objects.filter(user=user, is_active=True)
                for session in old_sessions:
                    session.end_session('forced')
            
            # Crear nueva sesión
            new_session = UserSession.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Login user for session authentication
            login(request, user)
            
            return Response({
                'message': 'Login exitoso',
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'session_id': new_session.id,
                'login_time': new_session.created_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            
            # Finalizar todas las sesiones activas del usuario
            # (o solo la actual si tenemos session_key)
            session_key = request.session.session_key
            if session_key:
                # Finalizar solo la sesión actual
                UserSession.objects.filter(
                    user=user,
                    session_key=session_key,
                    is_active=True
                ).update(
                    is_active=False,
                    ended_at=timezone.now(),
                    logout_type='manual'
                )
            else:
                # Si no hay session_key, finalizar la sesión más reciente
                recent_session = UserSession.objects.filter(
                    user=user,
                    is_active=True
                ).first()
                if recent_session:
                    recent_session.end_session('manual')
            
            # Delete user's token
            Token.objects.filter(user=user).delete()
            
            # Logout from Django session
            logout(request)
            
            return Response({
                'message': 'Logout exitoso',
                'user': user.email,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Error en logout: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """
    API endpoint for user profile management
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    API endpoint for changing password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            
            # Change password
            user.set_password(new_password)
            user.save()
            
            # Delete all tokens to force re-login
            Token.objects.filter(user=user).delete()
            
            # Deactivate all sessions
            UserSession.objects.filter(user=user).update(is_active=False)
            
            return Response({
                'message': 'Contraseña cambiada exitosamente. Debe iniciar sesión nuevamente.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API endpoint for password reset request
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate reset token
            user.password_reset_token = secrets.token_urlsafe(32)
            user.password_reset_token_created = timezone.now()
            user.save()
            
            # TODO: Send password reset email
            # self.send_password_reset_email(user)
            
            return Response({
                'message': 'Se ha enviado un email con instrucciones para restablecer la contraseña.',
                'reset_token': user.password_reset_token  # Remove in production
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_password_reset_email(self, user):
        """Send password reset email"""
        # TODO: Implement email sending
        pass


class PasswordResetConfirmView(APIView):
    """
    API endpoint for password reset confirmation
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Reset password
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_token_created = None
            user.save()
            
            # Delete all tokens
            Token.objects.filter(user=user).delete()
            
            # Deactivate all sessions
            UserSession.objects.filter(user=user).update(is_active=False)
            
            return Response({
                'message': 'Contraseña restablecida exitosamente. Puede iniciar sesión con su nueva contraseña.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionsView(APIView):
    """
    API endpoint for managing user sessions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's active sessions"""
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    def delete(self, request):
        """Terminate all other sessions"""
        current_session = request.session.session_key
        
        # Deactivate all other sessions
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(session_key=current_session).update(is_active=False)
        
        return Response({
            'message': 'Todas las demás sesiones han sido cerradas.'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_security_info(request):
    """
    Get user security information
    """
    user = request.user
    
    # Recent login attempts
    recent_attempts = LoginAttempt.objects.filter(
        email=user.email
    ).order_by('-attempted_at')[:10]
    
    # Active sessions
    active_sessions = UserSession.objects.filter(
        user=user,
        is_active=True
    ).count()
    
    return Response({
        'recent_login_attempts': LoginAttemptSerializer(recent_attempts, many=True).data,
        'active_sessions_count': active_sessions,
        'last_login': user.last_login,
        'last_login_ip': user.last_login_ip,
        'is_email_verified': user.is_email_verified,
        'date_joined': user.date_joined
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """
    Verify user email with token
    """
    token = request.data.get('token')
    
    if not token:
        return Response({
            'error': 'Token requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({
            'message': 'Email verificado exitosamente'
        })
        
    except User.DoesNotExist:
        return Response({
            'error': 'Token inválido'
        }, status=status.HTTP_400_BAD_REQUEST)


class SessionManagementView(APIView):
    """
    API endpoint for session management (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all sessions for admin review"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo administradores pueden acceder a esta información'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sessions = UserSession.objects.all().order_by('-created_at')
        
        session_data = []
        for session in sessions:
            duration = self.calculate_duration(session)
            session_info = {
                'id': session.id,
                'user': {
                    'email': session.user.email,
                    'name': session.user.get_full_name(),
                    'id': session.user.id
                },
                'ip_address': session.ip_address,
                'user_agent': session.user_agent[:100] + '...' if len(session.user_agent) > 100 else session.user_agent,
                'is_active': session.is_active,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'ended_at': session.ended_at,
                'logout_type': session.logout_type,
                'duration': duration,
                'session_key': session.session_key[:10] + '...' if session.session_key else None
            }
            session_data.append(session_info)
        
        # Statistics
        total_sessions = sessions.count()
        active_sessions = sessions.filter(is_active=True).count()
        inactive_sessions = total_sessions - active_sessions
        
        return Response({
            'sessions': session_data,
            'statistics': {
                'total': total_sessions,
                'active': active_sessions,
                'inactive': inactive_sessions,
                'users_with_sessions': sessions.values('user').distinct().count()
            }
        })
    
    def delete(self, request, session_id=None):
        """Force logout a specific session (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo administradores pueden realizar esta acción'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            session = UserSession.objects.get(id=session_id, is_active=True)
            session.end_session('forced')
            
            # Also invalidate the user's token if it exists
            Token.objects.filter(user=session.user).delete()
            
            return Response({
                'message': f'Sesión de {session.user.email} terminada forzosamente',
                'session_id': session_id
            })
        except UserSession.DoesNotExist:
            return Response(
                {'error': 'Sesión no encontrada o ya inactiva'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def calculate_duration(self, session):
        """Calculate session duration"""
        from django.utils import timezone
        
        if session.ended_at:
            duration = session.ended_at - session.created_at
        elif session.is_active:
            duration = timezone.now() - session.created_at
        else:
            duration = session.last_activity - session.created_at
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class UserSessionHistoryView(APIView):
    """
    API endpoint to get session history for a specific user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id=None):
        """Get session history for current user or specific user (admin only)"""
        
        # If user_id is provided, check admin permissions
        if user_id:
            if not request.user.is_staff:
                return Response(
                    {'error': 'Solo administradores pueden ver sesiones de otros usuarios'},
                    status=status.HTTP_403_FORBIDDEN
                )
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            target_user = request.user
        
        sessions = UserSession.objects.filter(user=target_user).order_by('-created_at')
        
        session_data = []
        for session in sessions:
            duration = SessionManagementView().calculate_duration(session)
            session_info = {
                'id': session.id,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': session.is_active,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'ended_at': session.ended_at,
                'logout_type': session.logout_type,
                'duration': duration
            }
            session_data.append(session_info)
        
        return Response({
            'user': {
                'id': target_user.id,
                'email': target_user.email,
                'name': target_user.get_full_name()
            },
            'sessions': session_data,
            'total_sessions': len(session_data),
            'active_sessions': sum(1 for s in session_data if s['is_active'])
        })
