from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login

from .forms.album_forms import (
    AlbumCollectionForm, 
    AlbumWishlistForm, 
    AlbumSearchForm, 
    AlbumUpdateForm,
)
from .domain.models import Album
from .domain.exceptions import (
    AlbumAlreadyInCollectionError, 
    AlbumAlreadyOnWishlistError,
    AlbumDoesNotExistError,
)
from . import constants

# Create your views here. (should be as easy as possible and call model and/or optional service layer logic)

# Django views return an HttpResponse object containing the content for requested page, or raise an excepiton like Http404,
# they don't care about anything else


class DetailView(LoginRequiredMixin, generic.DetailView):
    template_name = constants.DirPaths.TEMPLATES_PATH.file("detail.html")
    model = Album

    def get_queryset(self):
        auth_user = self.request.user
        domain_user = auth_user.albumz_user
        return domain_user.albums.all()
    

class EditView(LoginRequiredMixin, UpdateView):
    template_name = constants.DirPaths.FORM_PATH.file("album_update_form.html")
    model = Album
    form_class = AlbumUpdateForm

    def form_valid(self, form):
        domain_user = self.request.user.albumz_user
        edited_album = form.save(commit=False)
        try:
            domain_user.edit_album(self.object, edited_album)
        except AlbumAlreadyInCollectionError:
            form.add_error(None, constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR)
            return self.form_invalid(form)
        except AlbumAlreadyOnWishlistError:
            form.add_error(None, constants.ResponseStrings.ALBUM_ON_WISHLIST_ERROR)
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.is_in_collection():
            return reverse_lazy(constants.ReverseURLNames.COLLECTION)
        return reverse_lazy(constants.ReverseURLNames.WISHLIST)

    def get_queryset(self):
        domain_user = self.request.user.albumz_user
        return domain_user.albums.all()
    

def move_to_collection_view(request, pk):
    if request.user.is_authenticated:
        domain_user = request.user.albumz_user
        try:
            domain_user.move_to_collection(pk)
            return HttpResponseRedirect(reverse(constants.ReverseURLNames.COLLECTION))
        except AlbumDoesNotExistError:
            raise Http404()
        except AlbumAlreadyInCollectionError:
            return HttpResponseRedirect(reverse(constants.ReverseURLNames.DETAIL, args=(pk,)))
    else:
        return redirect_to_login(request.get_full_path())


@method_decorator(never_cache, name="dispatch")
class CollectionView(LoginRequiredMixin, generic.ListView):
    template_name = constants.DirPaths.TEMPLATES_PATH.file("collection.html")
    context_object_name = constants.TemplateContextVariables.ALBUMS_COLLECTION

    def get_queryset(self):
        domain_user = self.request.user.albumz_user
        queryset = domain_user.albums.in_collection()
        self.form = AlbumSearchForm(self.request.GET)
        if self.form.is_valid():
            queryset = queryset.search_query(self.form.cleaned_data["query"])
        return queryset


class WishlistView(LoginRequiredMixin, generic.ListView):
    template_name = constants.DirPaths.TEMPLATES_PATH.file("wishlist.html")
    context_object_name = constants.TemplateContextVariables.ALBUMS_WISHLIST

    def get_queryset(self):
        domain_user = self.request.user.albumz_user
        queryset = domain_user.albums.on_wishlist()
        self.form = AlbumSearchForm(self.request.GET)
        if self.form.is_valid():
            queryset = queryset.search_query(self.form.cleaned_data["query"])
        return queryset


class AlbumAddColletionView(LoginRequiredMixin, FormView):
    template_name = constants.DirPaths.FORM_PATH.file("album_creation_form.html")
    form_class = AlbumCollectionForm
    success_url = reverse_lazy(constants.ReverseURLNames.COLLECTION)

    def form_valid(self, form):
        domain_user = self.request.user.albumz_user
        album = form.save(commit=False)
        try:
            domain_user.add_to_collection(album)
        except AlbumAlreadyInCollectionError:
            form.add_error(None, constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR)
            return self.form_invalid(form)
        return super().form_valid(form)
        

class AlbumAddWishlistView(LoginRequiredMixin, FormView):
    template_name = constants.DirPaths.FORM_PATH.file("album_creation_form.html")
    form_class = AlbumWishlistForm
    success_url = reverse_lazy(constants.ReverseURLNames.WISHLIST)

    def form_valid(self, form):
        domain_user = self.request.user.albumz_user
        album = form.save(commit=False)
        try:
            domain_user.add_to_wishlist(album)
        except AlbumAlreadyInCollectionError:
            form.add_error(None, constants.ResponseStrings.ALBUM_IN_COLLECTION_ERROR)
            return self.form_invalid(form)
        except AlbumAlreadyOnWishlistError:
            form.add_error(None, constants.ResponseStrings.ALBUM_ON_WISHLIST_ERROR)
            return self.form_invalid(form)
        return super().form_valid(form)
    

class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Album

    def get_success_url(self):
        if self.object.is_in_collection():
            return reverse_lazy(constants.ReverseURLNames.COLLECTION)
        return reverse_lazy(constants.ReverseURLNames.WISHLIST)
    
    def get_queryset(self):
        domain_user = self.request.user.albumz_user
        return domain_user.albums.all()
    