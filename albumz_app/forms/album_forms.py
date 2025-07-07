from django import forms
from django.utils import timezone

from ..domain.models import Album


class AlbumSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Search")


class BaseAlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["title", "artist", "pub_date", "genre", "user_rating"]

    def clean_pub_date(self):
        pub_date = self.cleaned_data["pub_date"]
        if pub_date is None:
            return pub_date
        else:
            if pub_date > timezone.now().date():
                raise forms.ValidationError(
                    "Publication date cannot be in the future.",
                )
            return pub_date


class AlbumCollectionForm(BaseAlbumForm): ...


class AlbumWishlistForm(BaseAlbumForm): ...


class AlbumUpdateForm(BaseAlbumForm): ...
