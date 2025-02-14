from django.urls import path
from . import views
app_name = 'store'

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.all_products, name="all_products"),
    path("add_product/", views.add_product, name="add_product"),
]