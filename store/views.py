from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import MusicProduct, ElectronicProduct
from itertools import chain

def index(request):
    music_products = MusicProduct.objects.all()[:3]
    electronic_products = ElectronicProduct.objects.all()[:3]
    context = {
        'music_products': music_products,
        'electronic_products': electronic_products
    }
    return render(request, 'index.html', context)


def all_products(request):
    music_products = MusicProduct.objects.all()
    electronic_products = ElectronicProduct.objects.all()
    combined_products = list(chain(music_products, electronic_products))

    for product in music_products:
        product.product_type = 'music'
        
    for product in electronic_products:
        product.product_type = 'electronic'

    context = {
        'products': combined_products,
    }
    return render(request, 'products.html', context)