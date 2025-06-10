from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .domain.models import Artist, Album

# Create your views here. (should be as easy as possible and call model and/or optional service layer logic)

# Django views return an HttpResponse object containing the content for requested page, or raise an excepiton like Http404,
# they don't care about anything else

# present 5 latest added albums
class IndexView(generic.ListView):
    template_name = "albumz_app/index.html"
    context_object_name = "latest_albums"

    # defined get_queryset / get_object or overriden model class attribute are the only ways to tell generic views on what
    # model data they are operating
    # the name of resulting data is defined in context_object_name
    def get_queryset(self):
        return Album.objects.order_by("-add_date")[:5] # resulting object is a QuerySet, which is iterable

class DetailView(generic.DetailView):
    template_name = "albumz_app/detail.html"
    model = Album

    # this is the standard way to add variables to template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_choices"] = Album._meta.get_field('user_rating').choices
        return context

class ResultsView(generic.DetailView):
    template_name = "albumz_app/results.html"
    model = Artist

def rate(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    # user_rating on instance attribute will just give its int value, so in order to get the field attribute 
    # with things like choices, default and so on, you have to access the _meta.getfield of the model class like so:
    rating_choices = Album._meta.get_field('user_rating').choices
    # rating_choices is a list of 2-tuples, a 2-tuple is an iterable, so I can convert it to dict if necessary
    try:
        rating_value = int(request.POST["user_rating"]) # will raise KeyError if user_rating wasnt provided in the form data
    except (KeyError, Album.DoesNotExist):
        return render(
            request, 
            "albumz_app/detail.html", 
            {
                "album": album, 
                "rating_choices": rating_choices, 
                "error_message": "No rating given."
            }
        )
    else:
        album.user_rating = rating_value
        album.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("albumz:results", args=(album.artist.id,)))