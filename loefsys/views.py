"""Module containing the views."""

from django.shortcuts import redirect, render

from .profile.forms import SignupForm


def main(request):
    """View for loading the index page."""
    announcements = [
        {
            "header": "Vul je logboek in!",
            "text": "Je hebt je logboek voor Scylla van 11-11 nog niet ingevuld.",
        },
        {
            "header": "Zeilseizoen start weer!",
            "text": "Het zeilseizoen gaat weer van start",
        },
    ]
    return render(request, "main.html", {"announcements": announcements})

def signup(request):
    """Sign up page view."""
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("/")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})
