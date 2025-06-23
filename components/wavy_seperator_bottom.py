from django_components import Component, register, types


@register("wavy-seperator-bottom")
class WavySeperatorTop(Component):
    """Component for a wavy separator at the bottom of a section."""

    # language=HTML
    template: types.django_html = """
        <div class="wavy-seperator-bottom">
            <div class="wave-bot flipped"></div>
            <div class="content">
                {% slot "content" default / %}
            </div>
        </div>
    """

    # language=CSS
    css: types.css = """

        .wave-bot {
            position: relative;
            bottom: 0;
            z-index: 10;
            top: 1px;
            background-image: url('/media/wave3.svg');
            background-position: top center;
            background-size: cover; 
            background-repeat: no-repeat;
            height: 5vh;
            width: 100%;
        }

        .flipped {
            transform: rotate(180deg);
        }

        .content {
            background-color: var(--background-blue);
        }
    """

    # language=JS
    js: types.js = """

    """
