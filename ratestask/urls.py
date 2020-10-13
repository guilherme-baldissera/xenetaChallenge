from django.urls import path
from .views import get_average_prices, add_prices

urlpatterns = [
    path('rates/', get_average_prices),
    path('addprices/', add_prices),
]
