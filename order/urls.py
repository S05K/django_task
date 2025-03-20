from django.urls import path 
from .views import OrderCreateView, OrderPaginatedView

urlpatterns=[
    path("orders", OrderCreateView.as_view(), name="create-order"),
    path("orders/<int:order_id>", OrderCreateView.as_view(), name="order"),
    path("admin/orders", OrderPaginatedView.as_view(), name="get-order"),   
]