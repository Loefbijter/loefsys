
from django.contrib.auth.views import LoginView
from django.urls import include, path

from .views import ProfileView, UserProfileView

app_name = "members"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html", next_page="/"), name="login"),
    path("reset-password/", ProfileView.as_view(), name="reset-password"),

    path("profiles/", include([
        path("profile/", UserProfileView.as_view(), name="user-profile"),
        # path("profile/edit/", None, name="edit-profile"),

        # path("", None, name="memberlist"),
        path("profile/<slug:slug>/", ProfileView.as_view(), name="profile"),
    ])),
]
