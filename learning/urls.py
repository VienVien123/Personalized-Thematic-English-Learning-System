from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # API User
    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(),name='logout'),

    path('api/user/account/',views.UserAccountView.as_view(),name='account'),
    path('api/user/change-password/',views.ChangePasswordView.as_view(),name='change_password'),

    # User
    path('', views.home_page, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('change_password/', views.change_password_page, name='change_password_page'),
    path('user/account/', views.account_page, name='account_page'),

    # API Listening
    path('api/topics/listen/', views.TopicView.as_view(), name='topic-view'),
    path('api/topics/listen/<slug:topic_slug>/', views.TopicDetailView.as_view(), name='topic_detail'),
    path('api/topics/listen/<slug:topic_slug>/subtopics/<slug:subtopic_slug>/listen-and-type/', views.ListenAndTypeView.as_view(), name='listen-and-type'),
    path('api/topics/listen/<slug:topic_slug>/subtopics/<int:subtopic_id>/next-prev/', views.get_previous_next_subtopic, name='next_prev_subtopic'),
    
    # Listening
    path('topics/listen/', views.topics_view_page, name='topics_view_page'),   
    path('topics/listen/<slug:topic_slug>/',views.topic_detail_page, name='topics_detail_page'),
    path('topics/listen/<slug:topic_slug>/subtopics/<slug:subtopic_slug>/listen-and-type/', views.listen_and_type_page, name='listen_and_type_page'),

    # Grammar
    path('grammar/', views.grammar_page, name='grammar'),
]