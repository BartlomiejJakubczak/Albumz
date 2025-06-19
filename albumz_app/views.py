from django.views import generic
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import Http404

from django.contrib.auth.mixins import LoginRequiredMixin

from .domain.models import Album
from .domain.exceptions import AlbumDoesNotExistError

# Create your views here. (should be as easy as possible and call model and/or optional service layer logic)

# Django views return an HttpResponse object containing the content for requested page, or raise an excepiton like Http404,
# they don't care about anything else


class DetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "albumz_app/detail.html"
    model = Album

    def get_object(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        try:
            return domain_user.get_album(self.kwargs["pk"])
        except AlbumDoesNotExistError:
            raise Http404("Album not found in collection.")


@method_decorator(never_cache, name="dispatch")
class ResultsView(LoginRequiredMixin, generic.ListView):
    template_name = "albumz_app/results.html"
    context_object_name = "albums_in_collection"

    def get_queryset(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        return domain_user.albums.filter(owned=True)


class WishlistView(LoginRequiredMixin, generic.ListView):
    template_name = "albumz_app/wishlist.html"
    context_object_name = "albums_on_wishlist"

    def get_queryset(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        return domain_user.albums.filter(owned=False)
