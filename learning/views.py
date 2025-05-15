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
import re
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, ChangePasswordSerializer,
    TopicListenSerializer, SectionSerializer, SubtopicSerializer, AudioExerciseSerializer,
    TopicVocabSerializer, WordSerializer
)

from .models import (
    User, TopicListen, Section, Subtopic, AudioExercise, TopicVocab, Word
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

# ------------------ Web Pages ------------------
def topics(request):
    topics_list = TopicVocab.objects.all()
    return render(request, 'topics_vocab.html', {'topics_vocab': topics_list})

def vocabulary(request):
    jwt_authenticator = JWTAuthentication()
    user = None

    # Xác thực JWT từ Authorization header
    try:
        header = request.headers.get("Authorization", None)
        if header:
            # Header có dạng "Bearer <token>"
            token = header.split(" ")[1] if " " in header else header
            validated_token = jwt_authenticator.get_validated_token(token)
            user = jwt_authenticator.get_user(validated_token)
    except (InvalidToken, TokenError, IndexError, AttributeError):
        user = None

    return render(request, 'vocabulary.html', {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_API_KEY": settings.SUPABASE_API_KEY,
        "USER_ID": user.id if user else None
    })

# ------------------ API: USER WORDS ------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_words(request):
    url = f"{SUPABASE_URL}/rest/v1/learning_word?user_id=eq.{request.user.id}&select=*"
    r = requests.get(url, headers=HEADERS)
    return JsonResponse(r.json(), safe=False, status=r.status_code)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_word(request):
    try:
        # Đảm bảo request body là JSON
        print("Request Content-Type:", request.content_type)
        print("Raw Request Body:", request.body)

        if request.content_type != "application/json":
            return Response({"error": "Content-Type must be application/json"}, status=400)

        if not request.body:
            return Response({"error": "Request body cannot be empty"}, status=400)

        data = json.loads(request.body)
        
        # Tạo payload cho Supabase
        payload = {
            "user_id": request.user.id,
            "word": data.get("word"),
            "definition": data.get("definition", ""),
            "example": data.get("example", ""),
            "topic": data.get("topic", ""),
            "is_learned": False
        }

        print("Parsed Request Payload:", payload)

        # Gọi API Supabase
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/learning_word",
            headers=HEADERS,
            json=payload
        )

        # Debug request và response
        print("Supabase Request URL:", response.url)
        print("Supabase Response Status Code:", response.status_code)
        print("Supabase Response Text:", response.text)

        # Xử lý phản hồi từ Supabase
        if response.status_code in [200, 201]:
            try:
                return Response(response.json(), status=response.status_code)
            except json.JSONDecodeError:
                return Response({"error": "Invalid response from Supabase. Not JSON."}, status=500)
        else:
            return Response({
                "error": "Unable to add user word",
                "details": response.text
            }, status=response.status_code)

    except requests.RequestException as e:
        print("Error while connecting to Supabase:", str(e))
        return Response({"error": "Connection error to Supabase."}, status=500)
    except Exception as e:
        print("Internal Server Error:", str(e))
        return Response({"error": "Internal server error.", "details": str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_user_word(request, word_id):
    data = json.loads(request.body)
    payload = {
        "word": data.get("word"),
        "definition": data.get("definition"),
        "example": data.get("example"),
        "topic": data.get("topic"),
        "is_learned": data.get("is_learned", False)
    }
    url = f"{SUPABASE_URL}/rest/v1/learning_word?id=eq.{word_id}&user_id=eq.{request.user.id}"
    r = requests.patch(url, headers=HEADERS, json=payload)
    return JsonResponse({"status": "updated"} if r.status_code == 204 else r.text, status=r.status_code)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_word(request, word_id):
    url = f"{SUPABASE_URL}/rest/v1/learning_word?id=eq.{word_id}&user_id=eq.{request.user.id}"
    r = requests.delete(url, headers=HEADERS)
    return JsonResponse({"status": "deleted"} if r.status_code == 204 else r.text, status=r.status_code)

# ------------------ API: SYSTEM DATA (TOPICS & VOCABULARY) ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topics(request):
    topics_list = TopicVocab.objects.all()
    serializer = TopicVocabSerializer(topics_list, many=True)
    return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_vocabulary_by_topic(request, topic_name):
    url = f"{SUPABASE_URL}/rest/v1/vocabulary?topic=eq.{topic_name}&select=english,vietnamese,ipa,type"
    r = requests.get(url, headers=HEADERS)
    return JsonResponse(r.json(), safe=False, status=r.status_code)
    
@api_view(['GET'])
def get_words_by_topic(request, topic):
    print(topic)
    words = TopicVocab.objects.filter(topic=topic)
    if not words:
        return Response({'message': 'Không có từ vựng nào'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TopicVocabSerializer(words, many=True)
    print(serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_vocabulary(request):
    user = request.user  # JWT xác thực tự động lấy user
    print("Authenticated User:", user)
    
    words = Word.objects.filter(user=user)
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data, status=200)

@api_view(['POST'])
def add_word(request):
    if request.method == 'POST':
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TopicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # URL của bảng learning_topiclisten trên Supabase
        url = f"{SUPABASE_URL}/rest/v1/learning_topiclisten?select=*"
        headers = {
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return Response(data, status=200)
            else:
                return Response({
                    "error": "Unable to fetch data from Supabase",
                    "details": response.text
                }, status=response.status_code)
        except requests.RequestException as e:
            print("❌ Error while connecting to Supabase:", str(e))
            return Response({"error": "Connection error to Supabase."}, status=500)

class TopicDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, topic_slug, format=None):
        topic = get_object_or_404(TopicListen, slug=topic_slug)
        query = request.GET.get('q','')
        level = request.GET.get('level','all')

        sections = Section.objects.filter(topic=topic).prefetch_related('subtopics')

        for section in sections:
            subs = section.subtopics.all().order_by('id')

            should_filter = query or (level and level != 'all')

            if should_filter:
                if query:
                    subs = subs.filter(title__icontains=query)
                if level and level != 'all':
                    subs = subs.filter(level=level)
            section.filtered_subtopics = subs

        topic_data = TopicListenSerializer(topic).data
        return Response({
            'topic':topic_data,
            'sections':SectionSerializer(sections, many=True).data
        })

class ListenAndTypeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, topic_slug, subtopic_slug, format=None):
        topic = get_object_or_404(TopicListen, slug=topic_slug)
        subtopic = get_object_or_404(Subtopic, slug=subtopic_slug)
        exercises = AudioExercise.objects.filter(subtopic=subtopic).order_by('position')

        # Chúng ta trả về tên topic, subtopic, và các bài tập
        exercises_data = AudioExerciseSerializer(exercises, many=True).data
        
        return Response({
            'topic': {'name': topic.name, 'slug': topic.slug},
            'subtopic': SubtopicSerializer(subtopic).data,
            'exercises': exercises_data
        })
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_previous_next_subtopic(request, topic_slug, subtopic_id):
    topic = get_object_or_404(TopicListen, slug=topic_slug)
    current_subtopic = get_object_or_404(Subtopic, id=subtopic_id, topic=topic)

    previous_subtopic = Subtopic.objects.filter(topic=topic, id__lt=current_subtopic.id).order_by('-id').first()
    next_subtopic = Subtopic.objects.filter(topic=topic, id__gt=current_subtopic.id).order_by('id').first()

    return JsonResponse({
        'previous': {
            'id': previous_subtopic.id,
            'slug': previous_subtopic.slug,
            'url': f"/topics/listen/{topic.slug}/subtopics/{previous_subtopic.slug}/listen-and-type/"
        } if previous_subtopic else None,
        'next': {
            'id': next_subtopic.id,
            'slug': next_subtopic.slug,
            'url': f"/topics/listen/{topic.slug}/subtopics/{next_subtopic.slug}/listen-and-type/"
        } if next_subtopic else None
    })

# <Render templates HTML files>
def home_page(request):
    return render(request, 'home.html')

# User template
def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def change_password_page(request):
    return render(request, 'change_password.html')

def account_page(request):
    return render(request, 'user_account.html')

# Listen templates
def topics_view_page(request):
    return render(request, 'topics_view.html')

def topic_detail_page(request, topic_slug):
    topic = get_object_or_404(TopicListen,slug=topic_slug)
    sections = Section.objects.filter(topic=topic).prefetch_related('subtopics')
    return render(request, 'topic_detail.html', {'topic':topic, 'sections':sections})

def listen_and_type_page(request, topic_slug, subtopic_slug):
    topic = get_object_or_404(TopicListen, slug=topic_slug)
    subtopic = get_object_or_404(Subtopic, slug=subtopic_slug)

    exercises = AudioExercise.objects.filter(subtopic=subtopic).order_by('id','position')
    return render(
        request,
        'listen_and_type.html',
        {
            'topic':topic,
            'subtopic':subtopic,
            'exercises': exercises
        }
    )

def grammar_page(request):
    return render(request, 'grammar.html')
# </Render templates HTML files>


# Cấu hình Gemini
genai.configure(api_key="AIzaSyBg2npP92SnJRQwMSQAII_bPYeFyGh4ZCw")
model = genai.GenerativeModel("gemini-1.5-flash")
# Load model như trước
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load lại Chroma
vector_db = Chroma(persist_directory="./chroma_english_learning", embedding_function=embedding_model)
# @csrf_exempt
# def gemini_chat_view(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             message = data.get('message')
#             topic = data.get('topic', 'General')

#             system_prompt = f"You are an English learning assistant. Respond in a friendly, helpful way about: {topic}."
#             full_prompt = f"{system_prompt}\nUser: {message}\nAssistant:"

#             response = model.generate_content(full_prompt)
#             return JsonResponse({'response': response.text.strip()})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Invalid request'}, status=400)


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