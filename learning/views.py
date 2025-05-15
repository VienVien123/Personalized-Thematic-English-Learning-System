from django.shortcuts import render
from django.urls import path

# Create your views here.
def home_page(request):
    return render(request, 'home.html')
