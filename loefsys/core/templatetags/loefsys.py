"""Template tags module for not rendering blocks when certain apps aren't installed."""

from django import template
from django.apps import apps
from django.template import TemplateSyntaxError
from django.utils.text import unescape_string_literal

register = template.Library()


class RequireAppNode(template.Node):
    """Template node used to skip blocks that contain disabled apps.

    Helps with decoupling.
    """

    def __init__(self, app_name: str, nodelist: template.NodeList):
        assert isinstance(app_name, str)
        self.app_name = app_name
        self.nodelist = nodelist

    def render(self, context) -> str:
        """Render if the app is installed or return an empty string."""
        if apps.is_installed(self.app_name):
            return self.nodelist.render(context)
        return ""


@register.tag("requireapp")
def do_requireapp(parser, token):
    """TODO: Write documentation later, going to sleep now."""
    # token.split_contents returns ["requireapp", app_name]. As we do
    # {% requireapp "loefsys.core" %}, the second item contains the double quotes, which
    # must be stripped.
    bits = token.split_contents()
    if 2 < len(bits):  # noqa: PLR2004
        # Maybe we should remove PLR2004...
        raise TemplateSyntaxError(
            f"{bits[0]} takes only one argument, multiple arguments have been provided."
        )
    app_name = unescape_string_literal(bits[1])

    # Now we parse everything until the {% endrequireapp %} tag.
    nodelist = parser.parse(("endrequireapp",))

    # We skip the {% endrequireapp %} itself.
    parser.delete_first_token()  # Delete endrequireapp token

    return RequireAppNode(app_name, nodelist)
