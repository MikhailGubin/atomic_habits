from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пагинатор для вывода объектов 'Привычка'"""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
