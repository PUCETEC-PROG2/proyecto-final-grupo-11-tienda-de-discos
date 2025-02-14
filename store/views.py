from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from itertools import chain
from .models import MusicProduct, ElectronicProduct, Order
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

    page = request.GET.get('page', 1) 
    items_per_page = 10
    paginator = Paginator(combined_products, items_per_page)
    
    try:
        music = paginator.page(page)
    except PageNotAnInteger:
        music = paginator.page(1)
    except EmptyPage:
        music = paginator.page(paginator.num_pages)

    context = {
        'products': combined_products,
        'paginator': paginator,
    }
    return render(request, 'products.html', context)


def music_product(request):
    music_product = MusicProduct.objects.order_by('title')
    for product in music_product:
        product.product_type = 'music'
    
    page = request.GET.get('page', 1) 
    items_per_page = 10
    paginator = Paginator(music_product, items_per_page)
    
    try:
        music = paginator.page(page)
    except PageNotAnInteger:
        music = paginator.page(1)
    except EmptyPage:
        music = paginator.page(paginator.num_pages)
    
    context = {
        'products': music,
        'paginator': paginator
    }
    return render(request, 'music.html', context)

def electronic_product(request):
    electronic_product = ElectronicProduct.objects.order_by('name')
    for product in electronic_product:
        product.product_type = 'electronic'
    
    page = request.GET.get('page', 1) 
    items_per_page = 10
    paginator = Paginator(electronic_product, items_per_page)
    
    try:
        electronic = paginator.page(page)
    except PageNotAnInteger:
        electronic = paginator.page(1)
    except EmptyPage:
        electronic = paginator.page(paginator.num_pages)
    
    context = {
        'products': electronic,
        'paginator': paginator
    }
    return render(request, 'electronic.html', context)

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

def view_orders(request):
    orders = Order.objects.all()

    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)