from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status

from .models import BlacklistedToken
from .serializers import UserSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from product.models import Product
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.


class UserView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                response_data = {
                    "message": "User created successfully",
                    "user_id": user.id  # Ensure this field exists
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=409)
        
        except IntegrityError:
            return Response({"error": "User with this data already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



class LoginView(APIView):
    def post(self, request):
        """
        Authenticate user with email and password, and provide JWT token.
        """
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                user_role=False
                if user.is_authorized==True:
                    user_role='admin'
                else:
                    user_role='client'
                response_data = {
                    "token": access_token,
                    "refresh_token":str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "role": user_role,  # Assuming the user model has a `role` field
                        "name": f"{user.first_name} {user.last_name}"  # Assuming `first_name` & `last_name`
                    }
                }

                return Response(response_data, status=status.HTTP_200_OK)

            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            user_role = "admin" if request.user.is_authorized else "client"
            return Response({**serializer.data, "role": user_role}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

            return Response({"message": "Logout successful"}, status=200)

        except Exception as e:
            return Response({"error": "Invalid or expired token"}, status=400)
