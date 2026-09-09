from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by("id")
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CustomAuthToken(ObtainAuthToken):
    """Endpoint para autenticar y retornar el token en JSON."""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email},
            status=status.HTTP_200_OK,
        )
