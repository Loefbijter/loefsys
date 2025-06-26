"""Module defining the model for logs filled in by a user."""

from django.db import models

from loefsys.members.models.user import User


class UserLog(models.Model):
    """Stores a filled in log by a user.

    Attributes
    ----------
    user : ~loefsys.users.models.user.User
        The user that has filled in the user.
    filled_in : bool
        Flag which indicates whether the log was filled in.
    filled_in_at : ~datetime.datetime
        The timestamp the log was filled in.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filled_in = models.BooleanField()
    filled_in_at = models.DateTimeField()

    def __str__(self):
        return f"{self.log.name} {self.user.display_name}"
