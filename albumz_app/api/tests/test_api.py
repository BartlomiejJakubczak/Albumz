import pytest
from random import choice
from rest_framework.reverse import reverse
from rest_framework import status

from ...domain.models import Album
from ...constants import ReverseURLNames, ResponseStrings
from ...test_utils.utils import future_date


class TestAlbumsAPI:
    def strip_serializer_metadata(self, data):
        return {
            k: v for k, v in data.items()
            if k in {'title', 'artist', 'pub_date', 'genre', 'user_rating', 'owned'}
        }
    
    def test_album_list_view_requires_login(self, api_client):
        response = api_client.get(reverse(ReverseURLNames.API.ALBUMS))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_list_view_get(self, owned, auth_api_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        # When
        response = auth_api_client.get(reverse(ReverseURLNames.API.ALBUMS), format='json')
        # Then
        assert response.status_code == status.HTTP_200_OK
        for album_dict in list(response.data['results']):
            assert Album(**self.strip_serializer_metadata(album_dict)) in albums

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_list_view_post_successful(self, owned, auth_api_client, form_data_factory):
        # Given
        album_data = form_data_factory(owned=owned)
        # When
        response = auth_api_client.post(reverse(ReverseURLNames.API.ALBUMS), album_data, format='json')
        # Then
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_list_view_post_invalid_pub_date(self, owned, auth_api_client, form_data_factory):
        # Given
        album_data = form_data_factory(owned=owned, pub_date=future_date())
        # When
        response = auth_api_client.post(reverse(ReverseURLNames.API.ALBUMS), album_data, format='json')
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "pub_date" in response.data
        assert ResponseStrings.PUB_DATE_ERROR in response.data["pub_date"][0]

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_list_view_post_blank_pub_date(self, owned, auth_api_client, form_data_factory):
        # Given
        album_data = form_data_factory(owned=owned, pub_date=None)
        # When
        response = auth_api_client.post(reverse(ReverseURLNames.API.ALBUMS), album_data, format='json')
        # Then
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize("owned", [True, False])
    @pytest.mark.parametrize("field", ["title", "artist"])
    def test_album_list_view_post_blank_title_or_artist(self, owned, field, auth_api_client, form_data_factory):
        # Given
        kwargs = {field: None, "owned": owned}
        album_data = form_data_factory(**kwargs)
        # When
        response = auth_api_client.post(reverse(ReverseURLNames.API.ALBUMS), album_data, format='json')
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field in response.data
        assert "This field may not be blank" in response.data[field][0] or \
        "This field may not be null" in response.data[field][0]

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_detail_view_get(self, owned, auth_api_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        # When
        response = auth_api_client.get(reverse(ReverseURLNames.API.DETAIL, args=[chosen_album.pk]), format='json')
        # Then
        assert response.status_code == status.HTTP_200_OK
        assert chosen_album == Album(**self.strip_serializer_metadata(response.data))

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_detail_view_put_all_data_different(self, owned, auth_api_client, albums_factory, form_data_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        form_data = form_data_factory(owned=False if chosen_album.owned else True)
        # When
        response = auth_api_client.put(reverse(ReverseURLNames.API.DETAIL, args=[chosen_album.pk]), form_data, format='json')
        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == chosen_album.pk
        assert Album.albums.get(pk=response.data['id']) == Album(**form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_detail_view_put_same_artist_and_title(self, owned, auth_api_client, albums_factory, form_data_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        form_data = form_data_factory(
            title=chosen_album.title,
            artist=chosen_album.artist,
            owned=False if chosen_album.owned else True,
        )
        # When
        response = auth_api_client.put(reverse(ReverseURLNames.API.DETAIL, args=[chosen_album.pk]), form_data, format='json')
        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == chosen_album.pk
        assert Album.albums.get(pk=response.data['id']) == Album(**form_data)

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_detail_view_put_invalid_pub_date(self, owned, auth_api_client, albums_factory, form_data_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        form_data = form_data_factory(
            pub_date=future_date(),
            owned=owned,
        )
        # When
        response = auth_api_client.put(reverse(ReverseURLNames.API.DETAIL, args=[chosen_album.pk]), form_data, format='json')
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "pub_date" in response.data
        assert ResponseStrings.PUB_DATE_ERROR in response.data["pub_date"][0]

    @pytest.mark.parametrize("owned", [True, False])
    def test_album_detail_view_delete(self, owned, auth_api_client, albums_factory):
        # Given
        albums = albums_factory(owned=owned)
        chosen_album = choice(albums)
        # When
        response = auth_api_client.delete(reverse(ReverseURLNames.API.DETAIL, args=[chosen_album.pk]), format='json')
        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert chosen_album not in Album.albums.all()
