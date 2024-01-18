from django.shortcuts import render
from django.http import HttpResponse 

def home(request): 
    return HttpResponse('home')

def sobre(request):
    return HttpResponse('sobre')