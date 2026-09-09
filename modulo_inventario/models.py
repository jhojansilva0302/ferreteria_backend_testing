from django.db import models
from django.core.exceptions import ValidationError


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)
    precio_base = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)

    # Todos los métodos deben estar alineados a 4 espacios dentro de la clase:
    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock disponible no puede ser negativo.")

    def calcular_precio_con_iva(self):
        """Calcula el precio final con IVA del 19%."""
        return round(float(self.precio_base) * 1.19, 2)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
