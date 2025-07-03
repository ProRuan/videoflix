from django_filters import rest_framework as filters
from video_app.models import Video


class VideoFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre', lookup_expr='iexact')

    class Meta:
        model = Video
        fields = ['genre']
