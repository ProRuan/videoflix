# Third-party suppliers
from django_filters import rest_framework as filters

# Local imports
from video_app.models import Video


class VideoFilter(filters.FilterSet):
    """
    Represents a filter filtering videos by the field genre.
    """
    genre = filters.CharFilter(field_name='genre', lookup_expr='iexact')

    class Meta:
        model = Video
        fields = ['genre']
