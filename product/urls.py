from django.urls import path
from .views import CreateOrderView, AllDetailsView, CreateProductView

urlpatterns=[
    path("order", CreateOrderView.as_view(), name="create-order"),
    path("all", AllDetailsView.as_view(), name="all"),
    path("product/create", CreateProductView.as_view(), name="create-product"),
]