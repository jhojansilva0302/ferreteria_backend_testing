from django.test import TestCase
from django.core.exceptions import ValidationError
from modulo_inventario.models import Producto

class ProductoModelTests(TestCase):
    
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Martillo de Uña 16oz",
            codigo="FERR-001",
            precio_base=50000.00,
            stock=20
        )
        
    def test_calculo_precio_con_iva(self):
        """verifica que el calculo del 19% de IVA sea exacto."""
        precio_esperado = 59500.00 # 50000* 1.19
        self.assertEqual(self.producto.calcular_precio_con_iva(), precio_esperado)

    def test_validacion_stock_negativo(self):
        """Verifica que no se permita guardar un producto con stock negativo."""
        self.producto.stock = -5
        with self.assertRaises(ValidationError):
            self.producto.clean()
                