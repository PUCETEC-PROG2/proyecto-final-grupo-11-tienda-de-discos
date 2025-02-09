from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import MusicProduct, ElectronicProduct

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import MusicProduct, ElectronicProduct

def index(request):
    music_products = MusicProduct.objects.all()[:3]
    electronic_products = ElectronicProduct.objects.all()[:3]
    context = {
        'music_products': music_products,
        'electronic_products': electronic_products
    }
    return render(request, 'index.html', context)