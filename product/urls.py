from django.urls import path
from .views import (CartView, CreateOrderView, CreateProductView, CategoryListView, SubcategoryByCategoryView, ProductBySubcategoryView, ProductView, ProductDetail, CategoryCreateViewByAdmin,
                    ProductCreateViewByAdmin, SpecificPoductView)

urlpatterns=[
    path("order", CreateOrderView.as_view(), name="create-order"),
    path("product/create", CreateProductView.as_view(), name="create-product"),
    path("category", CategoryListView.as_view(), name="category"),
    path("sub-category/<int:category_id>",SubcategoryByCategoryView.as_view(), name="sub-category"),
    path("product-subcatgeory/<int:subcategory_id>",ProductBySubcategoryView.as_view(), name="product-subcatgeory"),
    path("products", ProductView.as_view(), name="products"),
    path("product-detail/<uuid:product_id>", ProductDetail.as_view(), name="product-detail"),
    path("cart", CartView.as_view(), name="cart"),
    path("cart/<int:cart_id>", CartView.as_view(), name="cart"),
    path("categories", CategoryCreateViewByAdmin.as_view(),name="categories"),
    path("admin/products", ProductCreateViewByAdmin.as_view(),name="products"),
    path("products/<int:product_id>", SpecificPoductView.as_view(), name="specific-product")
]
#/categories