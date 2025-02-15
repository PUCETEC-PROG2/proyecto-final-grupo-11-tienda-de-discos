from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from itertools import chain
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import MusicProduct, ElectronicProduct, Client, Order, OrderMusicItem, OrderElectronicItem
from .shopping_cart import ShoppingCart
from .pagination import PaginationMixin
from store.forms import ProductTypeForm, MusicProductForm, ElectronicProductForm, EditClientForm, OrderStatusForm, OrderMusicItemForm, OrderElectronicItemForm


def index(request):
    music_products = MusicProduct.objects.all()[:3]
    electronic_products = ElectronicProduct.objects.all()[:3]
    context = {
        'music_products': music_products,
        'electronic_products': electronic_products
    }
    return render(request, 'index.html', context)

###################### Vistas para gestionar productos ######################

class CustomLoginView(LoginView):
    template_name = "login_form.html"

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

@login_required
def add_product(request):
    type_form = ProductTypeForm(request.POST or None)
    music_form = MusicProductForm(request.POST or None, request.FILES or None)
    electronic_form = ElectronicProductForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if 'product_type' not in request.POST:
            messages.error(request, "Por favor seleccione un tipo de producto.")
        else:
            product_type = request.POST['product_type']
            
            if product_type == 'music':
                if music_form.is_valid():
                    try:
                        product = music_form.save()
                        messages.success(request, f"Producto musical '{product.name}' añadido exitosamente.")
                        return redirect('store:all_music')
                    except Exception as e:
                        messages.error(request, f"Error al guardar el producto: {str(e)}")
                else:
                    messages.error(request, "Por favor corrija los errores en el formulario de música.")
                    for field, errors in music_form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif product_type == 'electronic':
                if electronic_form.is_valid():
                    try:
                        product = electronic_form.save()
                        messages.success(request, f"Producto electrónico '{product.name}' añadido exitosamente.")
                        return redirect('store:all_electronic')
                    except Exception as e:
                        messages.error(request, f"Error al guardar el producto: {str(e)}")
                else:
                    messages.error(request, "Por favor corrija los errores en el formulario de electrónicos.")
                    for field, errors in electronic_form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
            else:
                messages.error(request, "Tipo de producto no válido.")
    
    context = {
        'type_form': type_form,
        'music_form': music_form,
        'electronic_form': electronic_form,
    }
    return render(request, 'add_product.html', context)

@login_required
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

@login_required
def add_client(request):
    if request.method == "POST":
        form = EditClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente añadido exitosamente.")
            return redirect('store:show_clients')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = EditClientForm()
    return render(request, 'add_client.html', {'form': form})



@login_required    
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

@login_required
def delete_client(request, pk):
    client = Client.objects.get(pk = pk)
    client.delete()
    return redirect('store:show_clients')

class CustomLoginView(LoginView):
    template_name = "login_form.html"

def view_orders(request):
    orders = Order.objects.all()
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)

@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    client_form = EditClientForm(request.POST or None, instance=order.client)

    if request.method == 'POST':
        if 'update_client' in request.POST:
            if client_form.is_valid():
                client_form.save()
                messages.success(request, "Datos del cliente actualizados exitosamente")
                return redirect('store:edit_order', order_id=order.id)
        elif 'cancel_order' in request.POST:
            try:
                # Restaurar stock de productos musicales
                for music_item in order.ordermusicitem_set.all():
                    product = music_item.product
                    product.stock += music_item.quantity
                    product.save()
                    music_item.delete()
                
                # Restaurar stock de productos electrónicos
                for electronic_item in order.orderelectronicitem_set.all():
                    product = electronic_item.product
                    product.stock += electronic_item.quantity
                    product.save()
                    electronic_item.delete()
                
                # Marcar orden como cancelada
                order.status = 'Cancelada'
                order.save()
                
                messages.success(request, "Orden cancelada y stock restaurado exitosamente")
                return redirect('store:view_orders')
                
            except Exception as e:
                messages.error(request, f"Error al cancelar la orden: {str(e)}")
        else:
            # Solo permitir cambiar el estado si no está cancelada
            if order.status != 'Cancelada':
                status_form = OrderStatusForm(request.POST, instance=order)
                if status_form.is_valid():
                    status_form.save()
                    messages.success(request, "Estado de la orden actualizado exitosamente")
                    return redirect('store:view_orders')
    
    # Si la orden está cancelada, mostrar mensaje informativo
    if order.status == 'Cancelada':
        messages.info(request, "Esta orden está cancelada. Para modificar los productos, por favor cree una nueva orden.")
    
    context = {
        'order': order,
        'status_form': OrderStatusForm(instance=order) if order.status != 'Cancelada' else None,
        'client_form': client_form,
        'music_items': order.ordermusicitem_set.all(),
        'electronic_items': order.orderelectronicitem_set.all(),
    }
    return render(request, 'edit_order.html', context)


def remove_order_item(request, order_id, item_id, item_type):
    order = get_object_or_404(Order, id=order_id)
    
    try:
        if item_type == 'music':
            item = get_object_or_404(OrderMusicItem, id=item_id, order=order)
            product = item.product
        else:
            item = get_object_or_404(OrderElectronicItem, id=item_id, order=order)
            product = item.product
            
        # Devolver el stock
        product.stock += item.quantity
        product.save()
        
        # Eliminar el item
        item.delete()
        
        messages.success(request, "Producto eliminado de la orden exitosamente")
        
    except Exception as e:
        messages.error(request, f"Error al eliminar el producto: {str(e)}")
        
    return redirect('store:edit_order', order_id=order_id)

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