from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=200)
    picture = models.ImageField(upload_to='products/', null=True, blank=True)
    class Meta:
        abstract = True

class MusicProduct(Product):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    release_date = models.DateField()
    GENRE_CHOICES = [
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('blues', 'Blues'),
        ('hiphop', 'Hip Hop'),
        ('reggae', 'Reggae'),
        ('metal', 'Metal'),
        ('classical', 'Classical'),
        ('country', 'Country'),
        ('folk', 'Folk'),
        ('latin', 'Latin'),
        ('electronic', 'Electronic'),
        ('otros', 'Otros')
    ]
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    FORMAT_CHOICES = [
        ('cd', 'CD'),
        ('vinyl', 'Vinilo'),
        ('cassete', 'Cassete')
    ]
    format = models.CharField(max_length=100, choices=FORMAT_CHOICES)
    def __str__(self):
        return f"{self.artist} - {self.title}"
    
class ElectronicProduct(Product):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    CATEGORY_CHOICES = [
        ('tocadiscos', 'Tocadiscos'),
        ('estereo', 'Estereo'),
        ('audifonos', 'Audifonos'),
        ('consola', 'Consola'),
        ('interfaces', 'Interfaces'),
        ('otros', 'Otros')
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField(max_length=200)
    def __str__(self):
        return f"{self.brand} - {self.model}"

class Client(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.name} {self.last_name}"    

    
class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('en camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')
    music_products = models.ManyToManyField(MusicProduct, through='OrderMusicItem')
    electronic_products = models.ManyToManyField(ElectronicProduct, through='OrderElectronicItem')

    @property
    def subtotal_amount(self):
        music_total = sum(item.quantity * item.unit_price for item in self.ordermusicitem_set.all())
        electronic_total = sum(item.quantity * item.unit_price for item in self.orderelectronicitem_set.all())
        return music_total + electronic_total

    @property
    def total_amount(self):
        subtotal = self.subtotal_amount
        iva = subtotal * Decimal('0.15')
        return subtotal + iva

    def __str__(self):
        return f"Orden {self.id} - {self.client.name} {self.client.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

class OrderMusicItem(OrderItem):
    product = models.ForeignKey(MusicProduct, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)

class OrderElectronicItem(OrderItem):
    product = models.ForeignKey(ElectronicProduct, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)