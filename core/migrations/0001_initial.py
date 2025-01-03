# Generated by Django 5.1.2 on 2024-12-06 14:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('marca', models.CharField(max_length=100)),
                ('modelo', models.CharField(default=0, max_length=100)),
                ('cantidad', models.PositiveIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.TextField()),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('id_qr', models.IntegerField(unique=True)),
                ('cod_producto', models.IntegerField()),
                ('creado_por', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='productos_creados', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductoUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_qr', models.IntegerField(default=0, unique=True)),
                ('cod_producto2', models.IntegerField(default=0)),
                ('cantidad', models.PositiveIntegerField(default=0)),
                ('fecha_modificacion', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
