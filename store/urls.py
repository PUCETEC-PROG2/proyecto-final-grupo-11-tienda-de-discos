from django.urls import path
from . import views
app_name = 'store'

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.all_products, name="all_products"),
    path("music/", views.music_product, name="all_music"),
    path("electronic/", views.electronic_product, name="all_electronic"),
    path("show_clients/", views.client_list, name="show_clients"),
    path("add_client/", views.add_client, name="add_client"),
    path("edit_client/<int:pk>", views.edit_client, name="edit_client"),
    path("delete_client/<int:pk>", views.delete_client, name="delete_client"),
    path("orders/", views.view_orders, name="view_orders"),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('decrement-from-cart/<int:pk>/', views.decrement_from_cart, name='decrement_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('edit-music/<int:pk>/', views.edit_product, {'product_type': 'music'}, name='edit_music'),
    path('edit-electronic/<int:pk>/', views.edit_product, {'product_type': 'electronic'}, name='edit_electronic'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit-order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('remove-order-item/<int:order_id>/<int:item_id>/<str:item_type>/',views.remove_order_item, name='remove_order_item'),
    path('login/', views.CustomLoginView.as_view(), name='login')
]

