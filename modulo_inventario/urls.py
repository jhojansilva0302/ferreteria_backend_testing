from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/auth/", CustomAuthToken.as_view(), name="api_auth"),
    path("api/v1/auth/token/", CustomAuthToken.as_view(), name="api_token"),
]

