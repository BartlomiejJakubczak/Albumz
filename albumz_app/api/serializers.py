from django.utils import timezone
from rest_framework import serializers

from ..constants import ResponseStrings, ReverseURLNames
from ..domain.models import Album, Genre


def validate_pub_date(value):
    if value is None:
        return value
    if value > timezone.now().date():
        raise serializers.ValidationError(ResponseStrings.PUB_DATE_ERROR)
    return value


class AlbumListSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedIdentityField(
        view_name=ReverseURLNames.API.DETAIL, read_only=True
    )

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "artist",
            "pub_date",
            "genre",
            "user_rating",
            "owned",
            "details",
        ]

    def validate_pub_date(self, value):
        return validate_pub_date(value)


class AlbumDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["id", "title", "artist", "pub_date", "genre", "user_rating", "owned"]
        read_only_fields = ["owned"]

    def validate_pub_date(self, value):
        return validate_pub_date(value)


class GenreFilterSerializer(serializers.Serializer):
    genre = serializers.ChoiceField(choices=Genre.choices, required=False)

    def validate_genre(self, value):
        return value.upper()
