
from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('customers/', views.CustomerListCreateView.as_view()),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view()),

    # Food Items
    path('food-items/', views.FoodItemListCreateView.as_view()),
    path('food-items/<int:pk>/', views.FoodItemDetailView.as_view()),

    # Orders
    path('orders/', views.OrderListCreateView.as_view()),
    path('orders/<int:pk>/', views.OrderDetailView.as_view()),

    # Order Items
    path('order-items/', views.OrderItemListCreateView.as_view()),
    path('order-items/<int:pk>/', views.OrderItemDetailView.as_view()),
]