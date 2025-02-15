from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from itertools import chain
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import MusicProduct, ElectronicProduct, Client, Order, OrderMusicItem, OrderElectronicItem
from .shopping_cart import ShoppingCart
from .pagination import PaginationMixin
from store.forms import ProductTypeForm, MusicProductForm, ElectronicProductForm, EditClientForm, OrderStatusForm, OrderMusicItemForm, OrderElectronicItemForm


def index(request):
    # Obtener productos agotados (stock = 0)
    out_of_stock_music = MusicProduct.objects.filter(stock=0)
    out_of_stock_electronic = ElectronicProduct.objects.filter(stock=0)
    
    # Obtener productos destacados (los 3 más recientes)
    featured_music = MusicProduct.objects.filter(stock__gt=0).order_by('-id')[:3]
    featured_electronic = ElectronicProduct.objects.filter(stock__gt=0).order_by('-id')[:3]
    
    # Obtener pedidos pendientes
    pending_orders = Order.objects.filter(status='pendiente')[:3]
    
    context = {
        'featured_music': featured_music,
        'featured_electronic': featured_electronic,
        'out_of_stock_music': out_of_stock_music,
        'out_of_stock_electronic': out_of_stock_electronic,
        'pending_orders': pending_orders
    }
    return render(request, 'index.html', context)

###################### Vistas para gestionar productos ######################

class CustomLoginView(LoginView):
    template_name = "login_form.html"

def all_products(request):
    pagination = PaginationMixin()
    music_products = MusicProduct.objects.all()
    electronic_products = ElectronicProduct.objects.all()
    
    # Búsqueda
    search_query = request.GET.get("q")
    if search_query:
        music_products = music_products.filter(
            Q(title__icontains=search_query) |
            Q(artist__icontains=search_query)
        )
        electronic_products = electronic_products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    # Ordenamiento
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        music_products = music_products.order_by('price')
        electronic_products = electronic_products.order_by('price')
    elif sort == 'price_desc':
        music_products = music_products.order_by('-price')
        electronic_products = electronic_products.order_by('-price')
    else:
        music_products = music_products.order_by('title')
        electronic_products = electronic_products.order_by('name')

    # Asignar tipo de producto
    for product in music_products:
        product.product_type = 'music'
    for product in electronic_products:
        product.product_type = 'electronic'

    combined_products = list(chain(music_products, electronic_products))
    products_page, paginator = pagination.paginate_queryset(combined_products, request)
    
    context = {
        'products': products_page,
        'paginator': paginator,
        'search_query': search_query,
        'current_sort': sort,
    }
    return render(request, 'products.html', context)


def music_product(request):
    pagination = PaginationMixin()
    music_products = MusicProduct.objects.order_by('title')
    
    search_query = request.GET.get("q")
    
    if search_query:
        music_products = music_products.filter(
            Q(title__icontains=search_query) |
            Q(artist__icontains=search_query) |
            Q(genre__icontains=search_query)
        )
    
    for product in music_products:
        product.product_type = 'music'
    
    products_page, paginator = pagination.paginate_queryset(music_products, request)
    
    context = {
        'products': products_page,
        'paginator': paginator,
        'search_query': search_query,
    }
    return render(request, 'music.html', context)

def electronic_product(request):
    pagination = PaginationMixin()
    electronic_products = ElectronicProduct.objects.all()
    
    # Búsqueda
    search_query = request.GET.get("q")
    if search_query:
        electronic_products = electronic_products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query)
        )
    
    # Filtros
    brand = request.GET.get('brand')
    sort = request.GET.get('sort')
    
    if brand:
        electronic_products = electronic_products.filter(brand=brand)

    
    # Ordenamiento
    if sort == 'price_asc':
        electronic_products = electronic_products.order_by('price')
    elif sort == 'price_desc':
        electronic_products = electronic_products.order_by('-price')
    else:
        electronic_products = electronic_products.order_by('name')
    
    for product in electronic_products:
        product.product_type = 'electronic'
    
    products_page, paginator = pagination.paginate_queryset(electronic_products, request)
    
    context = {
        'products': products_page,
        'paginator': paginator,
        'search_query': search_query,
        'current_brand': brand,
        'current_sort': sort,
        'brands': ElectronicProduct._meta.get_field('brand').choices,
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
    clients = Client.objects.all()
    
    # Búsqueda usando search_bar
    search_query = request.GET.get("q")
    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Solo ordenamiento
    sort = request.GET.get('sort')
    if sort == 'name':
        clients = clients.order_by('name')
    elif sort == '-name':
        clients = clients.order_by('-name')
    elif sort == 'email':
        clients = clients.order_by('email')
    else:
        clients = clients.order_by('name')
    
    clients_page, paginator = pagination.paginate_queryset(clients, request)
    
    context = {
        'clients': clients_page,
        'paginator': paginator,
        'search_query': search_query,
        'current_sort': sort
    }
    return render(request, 'show_clients.html', context)

@login_required
def add_client(request):
    if request.method == "POST":
        id_number = request.POST.get('id_number')
        # Verificar si existe un cliente con el mismo id_number
        existing_client = Client.objects.filter(id_number=id_number).first()
        
        if existing_client:
            messages.warning(
                request, 
                f"Ya existe un cliente con el número de identificación {id_number}: {existing_client.name} {existing_client.last_name}"
            )
            return render(request, 'add_client.html', {'form': EditClientForm(request.POST)})
        
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
    client = get_object_or_404(Client, pk=pk)
    client_form = EditClientForm(request.POST or None, instance=client)
    
    if request.method == 'POST' and client_form.is_valid():
        client_form.save()
        messages.success(request, "Cliente actualizado exitosamente.")
        return redirect('store:show_clients') 
    
    return render(request, 'edit_client.html', {
        'client_form': client_form,
        'client': client
    })

@login_required
def delete_client(request, pk):
    client = Client.objects.get(pk = pk)
    client.delete()
    return redirect('store:show_clients')

class CustomLoginView(LoginView):
    template_name = "login_form.html"

def view_orders(request):
    pagination = PaginationMixin()
    orders = Order.objects.all()
    
    # Búsqueda usando search_bar
    search_query = request.GET.get("q")
    if search_query:
        orders = orders.filter(
            Q(client__name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Filtros adicionales
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    sort = request.GET.get('sort')
    if sort == 'date_asc':
        orders = orders.order_by('created_at')
    elif sort == 'date_desc':
        orders = orders.order_by('-created_at')
    else:
        orders = orders.order_by('-created_at')
    
    orders_page, paginator = pagination.paginate_queryset(orders, request)
    
    context = {
        'orders': orders_page,
        'paginator': paginator,
        'search_query': search_query,
        'current_status': status,
        'current_sort': sort,
        'status_choices': Order._meta.get_field('status').choices
    }
    return render(request, 'orders.html', context)

@login_required
def show_order(request, pk):  # Cambia order_id por pk
    order = get_object_or_404(Order, id=pk)
    
    # Obtener los items de la orden
    music_items = order.ordermusicitem_set.all()
    electronic_items = order.orderelectronicitem_set.all()
    
    # Calcular total
    total = sum(item.quantity * item.unit_price for item in music_items) + \
            sum(item.quantity * item.unit_price for item in electronic_items)
    
    context = {
        'order': order,
        'music_items': music_items,
        'electronic_items': electronic_items,
        'total': total
    }
    return render(request, 'show_order.html', context)


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
    # Limpiar mensajes anteriores
    storage = messages.get_messages(request)
    for _ in storage:
        pass  

    if not cart.cart:
        messages.error(request, "El carrito está vacío")
        return redirect('store:cart_detail')
    
    # Procesar verificación de cliente existente
    if request.method == "POST":
        client_type = request.POST.get('client_type')
        
        if client_type == 'existing':
            id_number = request.POST.get('id_number')
            if id_number:
                existing_client = Client.objects.filter(id_number=id_number).first()
                if existing_client:
                    try:
                        order = create_order_for_client(existing_client, cart)
                        cart.clear()
                        messages.success(request, "¡Orden creada exitosamente!")
                        return redirect('store:show_order', pk=order.id) 
                    except Exception as e:
                        messages.error(request, f"Error al procesar la orden: {str(e)}")
                else:
                    messages.warning(request, "Cliente no encontrado. Por favor regístrese como cliente nuevo.")
                    return render(request, 'checkout.html', {
                        'cart': cart,
                        'show_full_form': True,
                        'client_form': EditClientForm(initial={'id_number': id_number})
                    })
        elif client_type == 'new':
            # Mostrar el formulario completo para nuevo cliente
            return render(request, 'checkout.html', {
                'cart': cart,
                'show_full_form': True,
                'client_form': EditClientForm()
            })
    
    # Primera carga de la página
    context = {
        'cart': cart,
        'show_full_form': False,
        'client_form': EditClientForm()
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
            order = create_order_for_client(client, cart)
            cart.clear()
            messages.success(request, "¡Orden creada exitosamente!")
            return redirect('store:show_order', pk=order.id)  
        except Exception as e:
            messages.error(request, f"Error al procesar la orden: {str(e)}")
    else:
        messages.error(request, "Por favor corrija los errores en el formulario")
    
    return render(request, 'checkout.html', {
        'cart': cart,
        'client_form': client_form,
        'show_full_form': True
    })

def create_order_for_client(client, cart):
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
    
    return order
