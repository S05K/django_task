from rest_framework.pagination import PageNumberPagination

class OrderPagination(PageNumberPagination):
    page_size = 5  # Number of products per page
    page_size_query_param = 'page_size'
    max_page_size = 20
