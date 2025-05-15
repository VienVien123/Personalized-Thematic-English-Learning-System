from django.shortcuts import render
from django.urls import path

# Create your views here.
def home_page(request):
    return render(request, 'home.html')
# grammar
def grammar_page(request):
    return render(request, 'grammar.html')