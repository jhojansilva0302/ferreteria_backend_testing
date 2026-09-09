from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ["id", "nombre", "codigo", "precio_base", "stock", "precio_final"]

    def get_precio_final(self, obj):
        return obj.calcular_precio_con_iva()

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock inicial no puede ser negativo.")
        return value
