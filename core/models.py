from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100) 
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, default=0)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos_creados', default=None)
    id_qr = models.IntegerField(max_length=50, unique=True)
    cod_producto = models.IntegerField()
    
    
class ProductoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) 
    id_qr = models.IntegerField(max_length=50, unique=True, default=0)
    cod_producto2 = models.IntegerField(default=0)
    cantidad = models.PositiveIntegerField(default=0)
    fecha_modificacion = models.DateTimeField(auto_now_add=True) 