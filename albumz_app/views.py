from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import DeleteView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms.album_forms import AlbumCollectionForm, AlbumWishlistForm
from .domain.models import Album
from .domain.exceptions import (
    AlbumDoesNotExistError, 
    AlbumAlreadyOwnedError, 
    AlbumAlreadyOnWishlistError,
)

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


@login_required
def add_album_collection(request):
    if request.method == "GET":
        return render(
            request,
            "albumz_app/forms/album_collection_form.html",
            {"form": AlbumCollectionForm()},
        )
    else:
        # POST
        domain_user = request.user.albumz_user
        form = AlbumCollectionForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            try:
                domain_user.add_to_collection(album)
            except AlbumAlreadyOwnedError:
                form.add_error(None, "You already own this album!")
                return render(
                    request,
                    "albumz_app/forms/album_collection_form.html",
                    {"form": form},
                )
            else:
                return HttpResponseRedirect(reverse("albumz:collection"))
        return render(
            request, "albumz_app/forms/album_collection_form.html", {"form": form}
        )


@login_required
def add_album_wishlist(request):
    if request.method == "GET":
        return render(
            request,
            "albumz_app/forms/album_wishlist_form.html",
            {"form": AlbumWishlistForm()},
        )
    else:
        # POST
        domain_user = request.user.albumz_user
        form = AlbumWishlistForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            try:
                domain_user.add_to_wishlist(album)
            except AlbumAlreadyOwnedError:
                form.add_error(None, "You already own this album!")
                return render(
                    request,
                    "albumz_app/forms/album_wishlist_form.html",
                    {"form": form},
                )
            except AlbumAlreadyOnWishlistError:
                form.add_error(None, "You already have this album on wishlist!")
                return render(
                    request,
                    "albumz_app/forms/album_wishlist_form.html",
                    {"form": form},
                )
            else:
                return HttpResponseRedirect(reverse("albumz:wishlist"))
        return render(
            request, "albumz_app/forms/album_wishlist_form.html", {"form": form}
        )
    

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
    