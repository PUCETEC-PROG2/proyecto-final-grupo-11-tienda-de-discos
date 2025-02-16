# Generated by Django 5.1.5 on 2025-01-24 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='electronicproduct',
            name='picture',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='musicproduct',
            name='picture',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('en camino', 'En camino'), ('entregado', 'Entregado'), ('cancelado', 'cancelado')], default='pendiente', max_length=20),
        ),
    ]
