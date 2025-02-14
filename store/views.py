from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from itertools import chain
from django.contrib import messages
from .models import MusicProduct, ElectronicProduct, Client, Order, OrderMusicItem, OrderElectronicItem
from .shopping_cart import ShoppingCart
from .pagination import PaginationMixin
from store.forms import ProductTypeForm, MusicProductForm, ElectronicProductForm, EditClientForm


def index(request):
    music_products = MusicProduct.objects.all()[:3]
    electronic_products = ElectronicProduct.objects.all()[:3]
    context = {
        'music_products': music_products,
        'electronic_products': electronic_products
    }
    return render(request, 'index.html', context)

###################### Vistas para gestionar productos ######################

def all_products(request):
    pagination = PaginationMixin()
    music_products = MusicProduct.objects.all()
    electronic_products = ElectronicProduct.objects.all()
    combined_products = list(chain(music_products, electronic_products))

    for product in music_products:
        product.product_type = 'music'
    for product in electronic_products:
        product.product_type = 'electronic'

    products_page, paginator = pagination.paginate_queryset(combined_products, request)
    
    context = {
        'products': products_page,
        'paginator': paginator,
    }
    return render(request, 'products.html', context)


def music_product(request):
    pagination = PaginationMixin()
    music_products = MusicProduct.objects.order_by('title')
    for product in music_products:
        product.product_type = 'music'
    
    products_page, paginator = pagination.paginate_queryset(music_products, request)
    
    context = {
        'products': products_page,
        'paginator': paginator
    }
    return render(request, 'music.html', context)

def electronic_product(request):
    pagination = PaginationMixin()
    electronic_products = ElectronicProduct.objects.order_by('name')
    for product in electronic_products:
        product.product_type = 'electronic'
    
    products_page, paginator = pagination.paginate_queryset(electronic_products, request)
    
    context = {
        'products': products_page,
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

def edit_product(request, pk, product_type):
    product = None
    form = None
    
    if product_type == 'music':
        product = get_object_or_404(MusicProduct, pk=pk)
        form = MusicProductForm(request.POST or None, request.FILES or None, instance=product)
        redirect_url = 'store:all_music'
    elif product_type == 'electronic':
        product = get_object_or_404(ElectronicProduct, pk=pk)
        form = ElectronicProductForm(request.POST or None, request.FILES or None, instance=product)
        redirect_url = 'store:all_electronic'
    else:
        messages.error(request, "Tipo de producto no válido")
        return redirect('store:all_products')
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{product.name} actualizado exitosamente.")
        return redirect(redirect_url)
    
    context = {
        'form': form,
        'product': product,
        'product_type': product_type
    }
    return render(request, 'edit_product.html', context)


#################### Logica para gestionar clientes y ordenes ####################

def client_list(request):
    pagination = PaginationMixin()
    clients = Client.objects.order_by('name')
    clients_page, paginator = pagination.paginate_queryset(clients, request)
    
    context = {
        'clients': clients_page,
        'paginator': paginator,
    }
    return render(request, 'show_clients.html', context)

    
def edit_client(request, pk):
    client = Client.objects.get(pk=pk)
    client_form = EditClientForm(request.POST or None, instance=client)
    storage = messages.get_messages(request)
    for _ in storage: 
        pass
    
    if request.method == 'POST' and client_form.is_valid():
        client_form.save()
        messages.success(request, "Cliente actualizado exitosamente.")
        return redirect('store:show_clients') 
    
    context = {
        'client_form': client_form,
        'client': client
    }
    return render(request, 'edit_client.html', context)

def view_orders(request):
    orders = Order.objects.all()
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)

####################### Vistas para gestionar el carrito de compras #######################
def add_to_cart(request, pk):
    cart = ShoppingCart(request)
    product = None
    
    try:
        product = MusicProduct.objects.get(pk=pk)
    except MusicProduct.DoesNotExist:
        try:
            product = ElectronicProduct.objects.get(pk=pk)
        except ElectronicProduct.DoesNotExist:
            messages.error(request, "Producto no encontrado.")
            return redirect(request.META.get('HTTP_REFERER'))

    if product.stock <= 0:
        messages.error(request, f"Lo sentimos, {product.name} está agotado.")
        return redirect(request.META.get('HTTP_REFERER'))

    if cart.add(product):
        messages.success(request, f"{product.name} añadido al carrito.")
    else:
        messages.error(request, f"No hay suficiente stock de {product.name}. Stock disponible: {product.stock}")
    
    return redirect(request.META.get('HTTP_REFERER'))
    
def cart_detail(request):
    cart = ShoppingCart(request)
    context = {
        'cart': cart
    }
    return render(request, 'cart_detail.html', context)

def remove_from_cart(request, pk):
    cart = ShoppingCart(request)
    product = None
    
    try:
        product = MusicProduct.objects.get(pk=pk)
    except MusicProduct.DoesNotExist:
        try:
            product = ElectronicProduct.objects.get(pk=pk)
        except ElectronicProduct.DoesNotExist:
            messages.error(request, "Producto no encontrado.")
            return redirect('store:cart_detail')
    
    cart.remove(product)
    messages.success(request, f"{product.name} eliminado del carrito.")
    return redirect('store:cart_detail')

def decrement_from_cart(request, pk):
    cart = ShoppingCart(request)
    product = None
    
    try:
        product = MusicProduct.objects.get(pk=pk)
    except MusicProduct.DoesNotExist:
        try:
            product = ElectronicProduct.objects.get(pk=pk)
        except ElectronicProduct.DoesNotExist:
            messages.error(request, "Producto no encontrado.")
            return redirect('store:cart_detail')
    
    cart.decrement(product)
    return redirect('store:cart_detail')

def clear_cart(request):
    cart = ShoppingCart(request)
    cart.clear()
    messages.success(request, "Carrito vaciado.")
    return redirect('store:cart_detail')

def checkout(request):
    cart = ShoppingCart(request)
    storage = messages.get_messages(request)
    for _ in storage: 
        pass
    
    if not cart.cart:
        messages.error(request, "El carrito está vacío")
        return redirect('store:cart_detail')
        
    client_form = EditClientForm(request.POST or None)
    
    context = {
        'cart': cart,
        'client_form': client_form,
    }
    return render(request, 'checkout.html', context)

def create_order(request):
    if request.method != 'POST':
        return redirect('store:checkout')
        
    cart = ShoppingCart(request)
    client_form = EditClientForm(request.POST)
    
    if client_form.is_valid():
        try:
            client = client_form.save()
            
            order = Order.objects.create(
                client=client,
                status='pendiente'
            )
            
            for item_id, item in cart.cart.items():
                try:
                    product = MusicProduct.objects.get(id=item['product_id'])
                    OrderMusicItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        unit_price=item['price']
                    )
                except MusicProduct.DoesNotExist:
                    try:
                        product = ElectronicProduct.objects.get(id=item['product_id'])
                        OrderElectronicItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item['quantity'],
                            unit_price=item['price']
                        )
                    except ElectronicProduct.DoesNotExist:
                        continue
                
                # Actualizar stock
                product.stock -= item['quantity']
                product.save()
            
            # Limpiar carrito
            cart.clear()
            messages.success(request, "¡Orden creada exitosamente!")
            return redirect('store:order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f"Error al procesar la orden: {str(e)}")
            return redirect('store:checkout')
    
    messages.error(request, "Por favor corrija los errores en el formulario")
    return redirect('store:checkout')