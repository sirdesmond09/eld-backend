"""
Pagination utilities for the Django Project Template.
"""

from rest_framework import pagination, status
from rest_framework.response import Response


class CustomLimitOffsetPagination(pagination.LimitOffsetPagination):
    """Custom pagination with limit and offset."""

    def __init__(self, default_limit=20):
        self.default_limit = default_limit

    def get_paginated_response(self, data):
        """Return paginated response."""
        data = {
            "count": self.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """Custom pagination with page numbers."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return paginated response."""
        response_data = {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CustomCursorPagination(pagination.CursorPagination):
    """Custom cursor-based pagination."""

    page_size = 20
    ordering = "-created_at"

    def get_paginated_response(self, data):
        """Return paginated response."""
        response_data = {
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
