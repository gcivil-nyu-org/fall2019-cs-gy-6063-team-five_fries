from mainapp.models import SiteUser
from location.models import Location
from review.models import Review

from .models import Review

from .form import ReviewForm


def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():

    else:
        form = ReviewForm()


