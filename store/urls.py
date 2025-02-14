from django.urls import path
from . import views
app_name = 'store'

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.all_products, name="all_products"),
    path("music/", views.music_product, name="all_music"),
    path("electronic/", views.electronic_product, name="all_electronic"),
    path("add_product/", views.add_product, name="add_product"),
]