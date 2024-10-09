from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_user.as_view(), name='register'),
    path('products/', view_products.as_view(), name='products'),
    path('cart/<int:pk>/', view_add_cart.as_view(), name = 'view_add_cart'),
    path('cart_item/<int:pk>/', remove_from_cart.as_view(), name='delete_cart_item'),
    path('order/', view_order.as_view(), name='view_orders'),
    path('order/<int:pk>/', view_single_order.as_view(), name='view_single_order'),
    path('checkout/<int:pk>/', checkout.as_view(), name='checkout'),
    path('webhook/', webhook, name='stripe_webhook'),
]