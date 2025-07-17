from rest_framework import serializers

from ..domain.models import Album, User


class AlbumSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'pub_date', 'genre', 'user_rating', 'owned', 'user']


class UserSerializer(serializers.ModelSerializer):
    albums = serializers.PrimaryKeyRelatedField(many=True, queryset=Album.albums.all())

    class Meta:
        model = User
        fields = ['id', 'auth_user', 'albums']