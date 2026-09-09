from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from modulo_inventario.models import Producto

class ProductoAPITestCase(APITestCase):
    
    def setUp(self):
        #crear Usuario y token
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.token = Token.objects.create(user=self.user)
        
        # Producto de prueba
        self.producto = Producto.objects.create(
            nombre="Taladro Percutor 800w",
            codigo="FERR-002",
            precio_base=250000.00,
            stock=10
        )
        self.url_list = "/api/v1/productos/"
        self.url_detail = f"/api/v1/productos/{self.producto.id}/"
        
    def test_obtener_productos_sin_autenticacion(self):
        """Lectura publica debe retornar 200ok."""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_crear_producto_sin_token_retorna_401(self):
        """Creacion no autorizada debe retornar 401 Unauthorized."""
        data = {
            "nombre": "Sierra Caladora",
            "codigo": "FERR-003",
            "precio_base": 180000.00,
            "stock": 5
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_crear_producto_con_token_exitoso(self):
        """creacion con token valido debe retornar 201 created."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            "nombre": "Cinta Metrica 5m",
            "codigo": "FERR-004",
            "precio_base": 150000.00,
            "stock": 50
            }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(),2)
        
    def test_crear_producto_datos_invalidos_retorna_400(self):
        """enviar stock negativo debe retornar 400 Bad request."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            "nombre": "Sierra Caladora",
            "codigo": "FERR-003",
            "precio_base": 180000.00,
            "stock": -5
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        