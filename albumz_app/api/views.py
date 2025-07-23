from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .serializers import AlbumSerializer
from ..constants import ResponseStrings, ReverseURLNames
from ..domain.models import Album
from ..domain.exceptions import (
    AlbumAlreadyInCollectionError, 
    AlbumAlreadyOnWishlistError,
)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        "albums": reverse(ReverseURLNames.API.ALBUMS, request=request, format=format),
    })


class AlbumsViewSet(viewsets.ModelViewSet):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        domain_user = self.request.user.albumz_user
        return domain_user.albums.order_by("artist", "title")

    def perform_create(self, serializer):
        domain_user = self.request.user.albumz_user
        data = serializer.validated_data
        album = Album(**data)
        try:
            if album.is_in_collection():
                domain_user.add_to_collection(album)
            elif album.is_on_wishlist():
                domain_user.add_to_wishlist(album)
        except AlbumAlreadyInCollectionError:
            raise ValidationError({"detail": ResponseStrings.ALBUM_IN_COLLECTION_ERROR})
        except AlbumAlreadyOnWishlistError:
            raise ValidationError({"detail": ResponseStrings.ALBUM_ON_WISHLIST_ERROR})
        else:
            serializer.instance = album
        
    def perform_update(self, serializer):
        domain_user = self.request.user.albumz_user
        edited_album = Album(**serializer.validated_data)
        try:
            domain_user.edit_album(self.get_object(), edited_album)
        except AlbumAlreadyInCollectionError:
            raise ValidationError({"detail": ResponseStrings.ALBUM_IN_COLLECTION_ERROR})
        except AlbumAlreadyOnWishlistError:
            raise ValidationError({"detail": ResponseStrings.ALBUM_ON_WISHLIST_ERROR})
        else:
            serializer.instance = self.get_object()

    @action(detail=True, methods=['get', 'post'], url_path='move-to-collection')
    def move_to_collection(self, request, pk=None):
        domain_user = request.user.albumz_user
        try:
            domain_user.move_to_collection(pk)
        except AlbumAlreadyInCollectionError:
            raise ValidationError({"detail": ResponseStrings.ALBUM_IN_COLLECTION_ERROR})
        else:
            return Response({"detail": ResponseStrings.MOVED_TO_COLLECTION}, status=status.HTTP_200_OK)
