from django_components import Component, register, types


@register("wavy-seperator-full")
class WavySeperatorTop(Component):
    """Component for a wavy separator for in between sections."""

    # language=HTML
    template: types.django_html = """
        <div class="flex flex-col items-center">
            {% component "wavy-seperator-bottom" / %}
            <div class="bg-secondary">
                {% slot "content" default / %}
            </div>
            {% component "wavy-seperator-top" / %}
        </div>
    """
