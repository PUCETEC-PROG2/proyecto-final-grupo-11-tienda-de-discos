# forms.py
from django import forms
from .models import MusicProduct, ElectronicProduct, Client

class ProductTypeForm(forms.Form):
    PRODUCT_TYPES = [
        ('music', 'Música'),
        ('electronic', 'Productos Electrónicos'),
    ]
    product_type = forms.ChoiceField(choices=PRODUCT_TYPES, widget=forms.RadioSelect)

class MusicProductForm(forms.ModelForm):
    class Meta:
        model = MusicProduct
        fields = ['name', 'price', 'description', 'picture', 'artist', 'title', 'release_date', 'genre', 'format']
        labels = {
            'name': 'Nombre',
            'price': 'Precio',
            'description': 'Descripción',
            'artist': 'Artista',
            'title': 'Título',
            'release_date': 'Fecha de Lanzamiento',
            'genre': 'Género',
            'format': 'Formato',
            'picture': 'Portada'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'artist': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ElectronicProductForm(forms.ModelForm):
    class Meta:
        model = ElectronicProduct
        fields = ['name', 'price', 'description', 'picture', 'brand', 'model', 'category']
        labels = {
            'name': 'Nombre',
            'price': 'Precio',
            'description': 'Descripción',
            'brand': 'Marca',
            'model': 'Modelo',
            'release_date': 'Fecha de Lanzamiento',
            'category': 'Categoría',
            'picture': 'Imagen',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class EditClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'last_name', 'email', 'phone', 'address']
        labels = {
            'name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }