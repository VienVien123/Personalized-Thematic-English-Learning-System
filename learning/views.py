import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import HttpResponse
from rest_framework import permissions, status, generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view, APIView, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings


import environ
from django.views.decorators.csrf import csrf_exempt

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, ChangePasswordSerializer
)

from .models import (
    User
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"  # Đảm bảo nội dung là JSON
}

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):

        # Proceed with the parent method to handle token generation
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # get email from form submission
        email = request.POST.get('email')
        if email:
            # Add user details to the response

            user = User.objects.get(email=email)
            user_serializer = UserSerializer(user)
            response.data['user'] = user_serializer.data

        return response

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            user.last_login = now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAccountView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request':self.request})
        return context
    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'Đổi mật khẩu thành công'}, status=status.HTTP_200_OK)
    
# <Render templates HTML files>
def home_page(request):
    return render(request, 'home.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def change_password_page(request):
    return render(request, 'change_password.html')

def account_page(request):
    return render(request, 'user_account.html')

def grammar_page(request):
    return render(request, 'grammar.html')


# Cấu hình Gemini
genai.configure(api_key="AIzaSyBg2npP92SnJRQwMSQAII_bPYeFyGh4ZCw")
model = genai.GenerativeModel("gemini-1.5-flash")
# Load model như trước
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load lại Chroma
vector_db = Chroma(persist_directory="./chroma_english_learning", embedding_function=embedding_model)

@csrf_exempt
def gemini_chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            topic = data.get('topic', 'General')

            # 🔍 RAG: truy xuất ngữ cảnh từ Chroma
            retrieved_docs = vector_db.similarity_search(message, k=4)
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            print("Retrieved Context:", context)
            # 🔧 Prompt
            prompt = f"""
You are an English learning assistant.
Use the context below to help the user with the topic: {topic}.

Context:
{context}

User: {message}
Assistant:
"""

            # 💬 Gửi vào Gemini
            response = model.generate_content(prompt)
            print("Gemini Response:", response.text.strip())
            cleaned = re.sub(r"\*+", "", response.text.strip())
            return JsonResponse({'response': cleaned})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def profile_view(request):
    return HttpResponse("You are logged in!")