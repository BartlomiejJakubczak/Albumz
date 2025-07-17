from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from ..domain.models import Album, User
from .serializers import AlbumSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        "users": reverse("api_user_list", request=request, format=format),
        "albums": reverse("api_album_list", request=request, format=format),
    })


class AlbumsList(generics.ListCreateAPIView):
    """
    List all albums, or create a new album.
    """
    queryset = Album.albums.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.albumz_user)


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an album.
    """
    queryset = Album.albums.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class UsersList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer