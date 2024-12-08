from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
import zipfile
from django.db.utils import IntegrityError
from PIL import Image
from datetime import datetime
import qrcode
import pandas as pd
import numpy as np
from .forms import CSVUploadForm
from django.views.decorators.csrf import csrf_exempt
from .models import Producto, ProductoUsuario
from django.db import connection
import os, io, shutil
from shutil import rmtree
import csv
from io import StringIO
import json
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

# Create your views here.
def home (request):
    return render(request, 'core/home.html')

def exit (request):
    logout(request)
    return redirect('home')

@login_required #decorador debe de ir por encima  de la definicion de la funcion
def products (request):
    if request.user.is_authenticated:
        registros = Producto.objects.filter(creado_por=request.user.id)
        return render(request, 'core/products.html', {'registros': registros})
    else:
        return redirect('login')
    
def generar_pdf(request, cod_producto):
    # Obtener el producto y su historial
    producto = Producto.objects.get(cod_producto=cod_producto)
    historial = ProductoUsuario.objects.filter(cod_producto2=cod_producto)
    costo_total = 0
    venta_total = 0

    # Crear el PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p = canvas.Canvas(buffer, pagesize=letter)
    # Título más grande y centrado
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(letter[0]/2, 780, f"Historial del producto: {producto.nombre} de {producto.marca} modelo {producto.modelo} ")

    # Crear una tabla simple con bordes
    p.setLineWidth(0.5)  # Ancho de las líneas
    p.setStrokeColor(colors.black)  # Color de las líneas

    # Cabeceras de la tabla
    p.setFont("Helvetica", 10)  # Reducir el tamaño de la fuente de las cabeceras
    p.drawString(50, 750, "Fecha")
    p.drawString(letter[0]/2, 750, "Valor")
    p.drawString(letter[0]-180, 750, "Cantidad")

    # Línea horizontal debajo de las cabeceras
    p.line(50, 745, letter[0]-50, 745)

    # Datos de la tabla
    y = 730
    for registro in historial:
        p.setFont("Helvetica", 10)  # Reducir el tamaño de la fuente de los datos
        p.drawString(50, y, f"{registro.fecha_modificacion}")
        if registro.id_qr>0:
            p.drawString(letter[0]/2, y, f"valor -{producto.precio*registro.cantidad}$")
            p.drawString(letter[0]-180, y, f"se aumentó en {registro.cantidad}")
        else:
            p.drawString(letter[0]/2, y, f"valor +{producto.precio_venta*registro.cantidad}$")
            p.drawString(letter[0]-180, y, f"disminuyó en {registro.cantidad}")
        p.line(50, y-5, letter[0]-50, y-5)
        y -= 20
    for registro in historial:
            if registro.id_qr > 0:
                costo_total += registro.cantidad * producto.precio
            else:
                venta_total += registro.cantidad * producto.precio_venta
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y-40, f"Costo total: {costo_total}")
    p.drawString(letter[0]/2, y-40, f"Venta total: {venta_total}")
    p.drawString(letter[0]-180, y-40, f"Beneficio neto: {venta_total - costo_total}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'historial_{producto.cod_producto}_{producto.nombre}_{producto.marca}_{producto.modelo}.pdf')

@login_required 
def scan_page(request):
    product_count = Producto.objects.filter(creado_por=request.user).count()
    if request.method == 'POST':
        try:           
            data = json.loads(request.body)

            # Parse the JSON data (assuming it's a valid JSON string)
            product_data = json.loads(data)

            cod_producto = product_data.get('id') 
            nombre = product_data.get('nombre')
            marca = product_data.get('marca')
            modelo = product_data.get('modelo')
            precio = product_data.get('precio')
            precio_venta = product_data.get('precio_venta')
            descripcion = product_data.get('descripcion')
            fecha_creacion = product_data.get('fecha_creacion')
            

            producto_existente = Producto.objects.filter(
                    cod_producto=cod_producto,
                    creado_por=request.user
                    ).first()

            if producto_existente:
                        return JsonResponse({'success': False, 'message': 'Producto ya registrado por ti.'}, status=400)
            else:
                # Crear un nuevo producto
                        producto = Producto(
                            cod_producto=cod_producto,
                            nombre=nombre,
                            marca=marca,
                            modelo=modelo,
                            cantidad=0,
                            descripcion=descripcion,
                            precio=precio,
                            precio_venta=precio_venta,
                            creado_por=request.user,
                            id_qr=(cod_producto*1000*request.user.id)  # Función para calcular el ID QR
                        )
                        producto.save()


                            # Prepare response data
            response_data = {
                        'success': True,
                        'contador': Producto.objects.filter(creado_por=request.user).count(),
                        'prodName': nombre,
                        'prodBrand': marca,
                        'prodModel': modelo,
                        'prodId': cod_producto
                    }

            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Código QR incompatible con Improvent®'})
    else:
        context = {'product_count': product_count}
        return render(request, 'core/scan_page.html', context)
    
    
@login_required 
def storage_page(request):
    product_count = Producto.objects.filter(creado_por=request.user).count()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_data = json.loads(data)

            # Extraer información del producto del JSON
            cantidad = product_data.get('cantidad')
            nombre = product_data.get('nombre')
            marca = product_data.get('marca')
            modelo = product_data.get('modelo')
            id_qr = product_data.get('id_qr')
            cod_producto = product_data.get('id')

            # Obtener el producto existente
            
            if id_qr < 0:
                return JsonResponse({'success': False, 'message': 'El Qr pertenece a ventas!'})
            
            try:
                producto = Producto.objects.get(cod_producto=cod_producto, creado_por=request.user)
            except Producto.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Producto no registrado o desconocido'})
            
            try:
                producto = ProductoUsuario.objects.get(id_qr=id_qr)
                return JsonResponse({'success': False, 'message': 'Qr ya usado'})
            
            except ProductoUsuario.DoesNotExist:
                
                producto.cantidad += cantidad
                producto.save()
            # Obtener o crear el registro de ProductoUsuario
                producto_usuario, created = ProductoUsuario.objects.get_or_create(
                usuario=request.user,
                producto=producto,
                cod_producto2=producto.cod_producto,
                id_qr=id_qr
            )

            # Actualizar la cantidad en ProductoUsuario
            producto_usuario.cantidad = cantidad
            producto_usuario.save()

            # Preparar la respuesta
            response_data = {
                'success': True,
                'message': 'Cantidad del producto actualizada correctamente',
                'prodName': nombre,
                'prodBrand': marca,
                'prodModel': modelo,
                'prodQty': cantidad,
                'prodId': cod_producto

            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Código QR incompatible con Improvent®'})
    else:
            context = {'product_count': product_count}
            return render(request, 'core/storage_page.html', context)

    
    
    
@login_required
def sales_page(request):
    product_count = Producto.objects.filter(creado_por=request.user).count()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_data = json.loads(data)

            # Extraer información del producto del JSON
            cantidad = product_data.get('cantidad')
            nombre = product_data.get('nombre')
            marca = product_data.get('marca')
            modelo = product_data.get('modelo')
            id_qr = product_data.get('id_qr')
            cod_producto = product_data.get('id')

            # Obtener el producto existente
            
            if id_qr > 0:
                return JsonResponse({'success': False, 'message': 'El Qr pertenece a Almacenamiento!'})
            
            try:
                producto = Producto.objects.get(cod_producto=cod_producto, creado_por=request.user)
            except Producto.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Producto no registrado o desconocido'})
                
            if cantidad > producto.cantidad:
                return JsonResponse({'success': False, 'message': 'La cantidad solicitada supera el stock disponible'})
            
            try:
                producto = ProductoUsuario.objects.get(id_qr=id_qr)
                return JsonResponse({'success': False, 'message': 'Qr ya usado'})
            
            except ProductoUsuario.DoesNotExist:
                
                producto.cantidad -= cantidad
                producto.save()
            # Obtener o crear el registro de ProductoUsuario
                producto_usuario, created = ProductoUsuario.objects.get_or_create(
                usuario=request.user,
                producto=producto,
                id_qr=id_qr
            )

            # Actualizar la cantidad en ProductoUsuario
            producto_usuario.cantidad = cantidad
            producto_usuario.save()

            # Preparar la respuesta
            response_data = {
                'success': True,
                'message': 'Cantidad del producto actualizada correctamente',
                'prodName': nombre,
                'prodBrand': marca,
                'prodModel': modelo,
                'prodQty': cantidad,
                'prodId': cod_producto

            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Código QR incompatible con Improvent®'})
    else:
            context = {'product_count': product_count}
            return render(request, 'core/sales_page.html', context)
    

@login_required
def csv_to_qr(request):
  if request.method == 'POST':
    form = CSVUploadForm(request.POST, request.FILES)
    if form.is_valid():
      csv_file = request.FILES['csv_file']
       # Leer el CSV
      data = pd.read_csv(csv_file)

      # Crear la carpeta temporal para guardar los QR
      temp_dir = 'temp_qr'
      os.makedirs(temp_dir, exist_ok=True)

      # Generar los códigos QR con datos JSON
      for index, row in data.iterrows():
        # Crear un diccionario con los datos del producto
        product_data = {
          "id": row['id'],
          "nombre": row['nombre'],
          "marca": row['marca'],
          "modelo": row['modelo'],
          "cantidad": row['cantidad'],
          "precio": row['precio'],
          "precio_venta": row['precio_venta'],
          "descripcion": row['descripcion'],
          "fecha_creacion": row['fecha_creacion'],
          "fecha_registro": row['fecha_registro'],
          "id_qr": row['id_qr'],
        }

        # Convertir el diccionario a formato JSON
        json_data = json.dumps(product_data)

        # Generar el código QR con los datos JSON
        img = qrcode.make(json_data)
        img.save(f"{temp_dir}/{row['id_qr']}_{row['nombre'].replace(' ', '_')}_{row['marca'].replace(' ', '_')}_{row['modelo'].replace(' ', '_')}.png")
        
        # Crear el archivo ZIP
      memory_file = io.BytesIO()
      with zipfile.ZipFile(memory_file, 'w') as zipf:
          for root, _, files in os.walk(temp_dir):
              for file in files:
                  zipf.write(os.path.join(root, file), file)

      # Eliminar la carpeta temporal
      rmtree(temp_dir)

      # Descargar el archivo ZIP
      response = HttpResponse(memory_file.getvalue(), content_type='application/zip')
      response['Content-Disposition'] = 'attachment; filename="codigos_qr.zip"' 

      return response

  else:
    form = CSVUploadForm()
  return render(request, 'core/csv_to_qr.html', {'form': form})





def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)
        
        if user_creation_form.is_valid():
            user_creation_form.save()
            
            user = authenticate(
                username=user_creation_form.cleaned_data['username'], 
                email=user_creation_form.cleaned_data['email'], 
                password=user_creation_form.cleaned_data['password1']
            )
            login(request, user)
            
            # Mensaje de éxito
            messages.success(request, 'Usuario nuevo creado con éxito.')
            
            return redirect('home')
        else:
            errors = user_creation_form.errors.as_data()
            for field, error_messages in errors.items():
                for error in error_messages:
                    if field == 'email':
                        messages.error(request, 'Por favor, introduce una dirección de correo electrónico válida.')
                    elif field == 'password1' and error.code == 'password_too_short':
                        messages.error(request, f'La contraseña debe tener al menos {user_creation_form.fields["password1"].min_length} caracteres.')
                    else:
                        messages.error(request, f'{field.title()}: {error}')
            return render(request, 'registration/register.html', {'form': user_creation_form})
    return render(request, 'registration/register.html', data)


def informe(request):
    if request.user.is_authenticated:
        registros = Producto.objects.filter(creado_por=request.user)
        return render(request, 'tu_template.html', {'registros': registros})
    else:
        return redirect('login')

