from django_components import Component, register, types

@register("wavy-seperator-full")
class WavySeperatorTop(Component):
    """Component for a wavy separator for in between sections."""

    # language=HTML
    template: types.django_html = """
        <div class="wavy-seperator-full">
            {% component "wavy-seperator-bottom" / %}
            {% slot "content" default / %}
            {% component "wavy-seperator-top" / %}
        </div>
    """

    # language=CSS
    css: types.css = """

    """

    # language=JS
    js: types.js = """

    """