from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import MusicProduct, ElectronicProduct
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from itertools import chain
from django.contrib import messages
from .models import MusicProduct, ElectronicProduct, Client
from store.forms import ProductTypeForm, MusicProductForm, ElectronicProductForm, EditClientForm


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



def client_list(request):
    clients = Client.objects.order_by('name')
    page = request.GET.get('page', 1) 
    items_per_page = 10
    paginator = Paginator(clients, items_per_page)
    
    try:
        clients_page = paginator.page(page)
    except PageNotAnInteger:
        clients_page = paginator.page(1)
    except EmptyPage:
        clients_page = paginator.page(paginator.num_pages)
    
    context = {
        'clients': clients_page,
        'paginator': paginator,
    }
    return render(request, 'show_clients.html', context)

    
def edit_client(request, pk):
    client = Client.objects.get(pk=pk)
    client_form = EditClientForm(request.POST or None, instance=client)
    
    if request.method == 'POST' and client_form.is_valid():
        client_form.save()
        messages.success(request, "Cliente actualizado exitosamente.")
        return redirect('store:show_clients') 
    
    context = {
        'client_form': client_form,
        'client': client
    }
    return render(request, 'edit_client.html', context)