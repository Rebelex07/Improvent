const productDetailsElement = document.getElementById('productDetails');

// Verificamos si el producto está registrado
if (document.getElementById('productRegistered')) {
  // Obtenemos el ID del producto de la respuesta del servidor (ajusta según tu estructura de datos)
  const productId = response_data.prodId;

  // Creamos un elemento de imagen
  const productImage = document.createElement('img');
  // Asignamos la ruta de la imagen según el ID del producto
  if (productId === '1') {
    productImage.src = STATIC_URL + 'custom/images/GRAFICA_GIGABYTE_RTX_4060.webp';
  } else if (productId === '2') {
    productImage.src = STATIC_URL + 'custom/images/otro_producto.jpg';
  } else {
    // Manejar otros casos, por ejemplo, mostrar una imagen por defecto
    productImage.src = STATIC_URL + 'custom/images/imagen_por_defecto.png';
  }

  // Creamos un elemento para mostrar el nombre del producto
  const productName = document.createElement('p');
  // Si mostramos la imagen, ocultamos el nombre
  if (productImage.src) {
    productName.textContent = '';
  } else {
    productName.textContent = response_data.productName; // Asigna el nombre del producto desde la respuesta
  }

  // Agregamos los elementos al contenedor de detalles del producto
  productDetailsElement.appendChild(productImage);
  productDetailsElement.appendChild(productName);
} else {
  // Si el producto no está registrado, mostramos un mensaje o realizamos otra acción
  productDetailsElement.textContent = 'Producto no encontrado';
}