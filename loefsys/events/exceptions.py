"""Custom exceptions for the events module."""


class RegistrationError(Exception):
    """Custom error for problems during registration."""


class NoUserObjectError(Exception):
    """Custom error for when no user object is found."""
