from rest_framework import serializers
from django.utils import timezone

from ..domain.models import Album
from ..constants import ReverseURLNames, ResponseStrings


class AlbumSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedIdentityField(view_name=ReverseURLNames.API.DETAIL, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'pub_date', 'genre', 'user_rating', 'owned', 'details']
        
    def validate_pub_date(self, value):
        if value is None:
            return value
        if value > timezone.now().date():
            raise serializers.ValidationError(ResponseStrings.PUB_DATE_ERROR)
        return value
