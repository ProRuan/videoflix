# Third-party suppliers
from rest_framework.pagination import PageNumberPagination


class VideoPagination(PageNumberPagination):
    """
    Represents a pagination for a video offer page.
    """
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100
