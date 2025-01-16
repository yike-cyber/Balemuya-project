import requests
import json
from django.core.cache import cache
from django.contrib.auth import login

from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

from django.conf import settings

from allauth.account.models import get_adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.models import SocialApp

from urllib.parse import parse_qs

from .models import User,ProfessionalProfile,CustomerProfile,AdminProfile
from .utils import send_sms,generate_otp,send_email_confirmation

from .serializers import UserSerializer,LoginSerializer,ProfessionalProfileSerializer,CustomerProfileSerializer,AdminProfileSerializer
class RegisterView(APIView):
    serializer_class = UserSerializer
    
    def post(self, request, *args, **kwargs):
        serializer_class = self.serializer_class
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user_instance = serializer.save()
            token = default_token_generator.make_token(user_instance)
            uid = urlsafe_base64_encode(str(user_instance.pk).encode())
            
            current_domain = request.get_host()
            verification_link = f'http://{current_domain}/api/users/auth/verify-email/?uid={uid}&token={token}'
            
            subject = 'Verify your email for Balemuya.'
            message = f'Please click the link below to verify your email for Balemuya.\n\n{verification_link}'
            recipient_list = [user_instance.email]
            
            # send confirmation email
            print('email send start')
            send_email_confirmation(subject, message,recipient_list)
            print('email send end')
            
            otp = generate_otp()
            cache.set(f"otp_{user_instance.email}", otp, timeout=300)
            
            cached = cache.get(f"otp_{user_instance.email}")
            print('cached otp',cached)
        
            phone_number = user_instance.phone_number
            message_body = f"Hello {user_instance.get_full_name()}, your OTP is {otp}. It is only valid for 5 minutes."
            send_sms(request, to=phone_number, message_body=message_body)
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailView(APIView):
    def get(self,request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk = uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyPhoneView(APIView):
    
    def post(self,request):
        otp = int( request.data.get('otp'))
        print('otp',otp)
        email = request.data.get('email')
        print('email',email)
        cached_otp = cache.get(f"otp_{email}")
        print('cached otp',cached_otp)
        
        if cached_otp == otp:
            print('otp is valid')
            user = User.objects.filter(email=email).first()
            user.is_active = True
            user.save()
            cache.delete(f"otp_{email}")
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP please type again.'}, status=status.HTTP_400_BAD_REQUEST)
        
        

class ResendOTPView(APIView):
    permission_classes = (AllowAny,)
    pass

class SetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        user = User.objects.filter(email=email).first()
        
        if user:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password set successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
        
            

class ResetPasswordView(APIView):
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = generate_otp()
            cache.set(f"otp_{user.email}", otp, timeout=300)
            phone_number = user.phone_number
            message_body = f"Hello {user.get_full_name()}, your OTP is {otp}. It is only valid for 5 minutes."
            send_sms(request, to=phone_number, message_body=message_body)
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email.'}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyPaswordResetOTPView(APIView):
    
    def post(self, request, *args, **kwargs):
        otp = int(request.data.get('otp'))
        email = request.data.get('email')
        cached_otp = cache.get(f"otp_{email}")
        if cached_otp == otp:
            return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP please type again.'}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        print('user',user.password)
        password = user.password
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not check_password(old_password, password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if old_password == new_password:
            return Response({'error': 'New password should be different from old password.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=user.id)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
    
class GoogleLoginCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')  
        state = request.GET.get('state', '{}')

        try:
            state = json.loads(state)
        except json.JSONDecodeError:
            return Response({'error': "Invalid state parameter"}, status=status.HTTP_400_BAD_REQUEST)

        if not code or not state:
            return Response({'error': "Missing code or state parameters"}, status=status.HTTP_400_BAD_REQUEST)

        user_type = state.get('user_type')
        if not user_type:
            return Response({'error': "Missing user_type in state parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': 'http://localhost:3000/google-callback',  # Set to your frontend redirect URI in development
                'grant_type': 'authorization_code',
            }
            token_response = requests.post(token_url, data=data)
            token_data = token_response.json()

            access_token = token_data.get('access_token')
            if not access_token:
                return Response({'error': "No access token received"}, status=status.HTTP_400_BAD_REQUEST)

            # Get user info from Google
            user_info_response = requests.get(
                'https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if user_info_response.status_code != 200:
                return Response({'error': user_info_response.json().get('error', 'Unknown error')}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_response.json()
            names = user_info.get('names', [{}])
            email_addresses = user_info.get('emailAddresses', [{}])

            first_name = names[0].get('givenName', '')
            last_name = names[0].get('unstructuredName', '')
            email = email_addresses[0].get('value', '')

            if not email:
                return Response({"error": "Email not found in user info"}, status=status.HTTP_400_BAD_REQUEST)

            # Create or retrieve the user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'password': 'temporarypassword123',
                    'is_active': True,
                    'user_type': user_type,
                }
            )

            # Generate access and refresh tokens
            access = AccessToken.for_user(user)
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(access),
                'refresh': str(refresh),
                'user_type': user.user_type
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = User.objects.filter(email=email).first()
        
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({'error': 'Your account is not active. Please check your email to verify your account.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user:
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)
            return Response({'message': 'Successfully logged in.',
                             "user":{
                            'email': user.email,
                            'user_type':user.user_type,
                            'access': access,
                            'refresh': refresh,
                            }
                            },status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({"error": "Authorization header with Bearer token is required."}, status=status.HTTP_400_BAD_REQUEST)

            access_token = auth_header.split(' ')[1]

            user = request.user

            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                if not BlacklistedToken.objects.filter(token=token).exists():
                    BlacklistedToken.objects.create(token=token)

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user is None:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.user_type == 'customer':
            
            customer = CustomerProfile.objects.filter(user=user).first()
            if customer is None:
                return Response({'error': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CustomerProfileSerializer(customer)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)
        
        if user.user_type =='professional':
            professional = ProfessionalProfile.objects.filter(user=user).first()
            if professional is None:
                return Response({'error': 'professional not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProfessionalProfileSerializer(professional)
            return Response({'user':serializer.data},status = status.HTTP_200_OK)
        
        if user.user_type == 'admin':
            admin = AdminProfile.objects.filter(user = user).first()
            serializer = AdminProfileSerializer(admin)
            return Response({'user':serializer.data},status = status.HTTP_200_OK)

        else:
            return Response({'error':'user not found'},status=status.HTTP_404_NOT_FOUND)
        


class UsersView(APIView):
    pass

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def get_serializer_class(self,request):
        pass
    
    def post(self,request,*args,**kwargs):
        
        if request.user is None:
            return Response({"message":"user not found"},status = status.HTTP_404_NOT_FOUND)
        if request.user.user_type =='customer':
            pass
        
        

