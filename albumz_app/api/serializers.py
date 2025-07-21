from rest_framework import serializers

from ..domain.models import Album


class AlbumSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='album-detail', read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'pub_date', 'genre', 'user_rating', 'owned',]
