from django.views import generic
from django.views.generic.edit import DeleteView, FormView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms.album_forms import AlbumCollectionForm, AlbumWishlistForm
from .domain.models import Album
from .domain.exceptions import (
    AlbumAlreadyInCollectionError, 
    AlbumAlreadyOnWishlistError,
)

# Create your views here. (should be as easy as possible and call model and/or optional service layer logic)

# Django views return an HttpResponse object containing the content for requested page, or raise an excepiton like Http404,
# they don't care about anything else


class DetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "albumz_app/detail.html"
    model = Album

    def get_queryset(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        return domain_user.albums.all()


@method_decorator(never_cache, name="dispatch")
class CollectionView(LoginRequiredMixin, generic.ListView):
    template_name = "albumz_app/collection.html"
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


class AlbumAddColletionView(LoginRequiredMixin, FormView):
    template_name = "albumz_app/forms/album_collection_form.html"
    form_class = AlbumCollectionForm
    success_url = reverse_lazy("albumz:collection")

    def form_valid(self, form):
        domain_user = self.request.user.albumz_user
        album = form.save(commit=False)
        try:
            domain_user.add_to_collection(album)
        except AlbumAlreadyInCollectionError:
            form.add_error(None, "You already own this album!")
            return self.form_invalid(form)
        return super().form_valid(form)
        

class AlbumAddWishlistView(LoginRequiredMixin, FormView):
    template_name = "albumz_app/forms/album_wishlist_form.html"
    form_class = AlbumWishlistForm
    success_url = reverse_lazy("albumz:wishlist")

    def form_valid(self, form):
        domain_user = self.request.user.albumz_user
        album = form.save(commit=False)
        try:
            domain_user.add_to_wishlist(album)
        except AlbumAlreadyInCollectionError:
            form.add_error(None, "You already own this album!")
            return self.form_invalid(form)
        except AlbumAlreadyOnWishlistError:
            form.add_error(None, "You already have this album on wishlist!")
            return self.form_invalid(form)
        return super().form_valid(form)
    

class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Album

    def get_success_url(self):
        if self.object.is_in_collection():
            return reverse_lazy("albumz:collection")
        return reverse_lazy("albumz:wishlist")
    
    def get_queryset(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        return domain_user.albums.all()
    