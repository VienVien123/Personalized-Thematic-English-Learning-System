from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    # Grammar
    path('grammar/', views.grammar_page, name='grammar'),
]
