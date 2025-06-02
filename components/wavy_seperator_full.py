from django_components import Component, register, types

@register("wavy-seperator-full")
class WavySeperatorTop(Component):
    """Component for a wavy separator for in between sections."""

    # language=HTML
    template: types.django_html = """
        <div class="wavy-seperator-full">
            {% component "wavy-seperator-bottom" / %}
            <div class="">
                {% slot "content" default / %}
            </div>
            {% component "wavy-seperator-top" / %}
        </div>
    """

    # language=CSS
    css: types.css = """
        /* .content {
            background-color: #1ab2e6;
            padding: 4px;
            outline-offset:-4px;
            outline: 4px solid #1ab2e6;
        } */
    """

    # language=JS
    js: types.js = """

    """