from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from itertools import chain

from .models import MusicProduct, ElectronicProduct
from store.forms import ProductTypeForm, MusicProductForm, ElectronicProductForm



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

def add_product(request):
    type_form = ProductTypeForm(request.POST or None)
    music_form = MusicProductForm(request.POST or None, request.FILES or None)
    electronic_form = ElectronicProductForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST' and 'product_type' in request.POST:
        if request.POST['product_type'] == 'music' and music_form.is_valid():
            music_form.save()
            messages.success(request, "Producto añadido exitosamente.")
            return redirect('music_products_list')
        elif request.POST['product_type'] == 'electronic' and electronic_form.is_valid():
            electronic_form.save()
            messages.success(request, "Producto añadido exitosamente.")
            return redirect('electronic_products_list')
    
    context = {
        'type_form': type_form,
        'music_form': music_form,
        'electronic_form': electronic_form,
    }
    return render(request, 'add_product.html', context)