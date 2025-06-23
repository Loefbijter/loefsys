from django_components import Component, register, types

@register("wavy-seperator-top")
class WavySeperatorTop(Component):
    """Component for a wavy separator at the top of a section."""

    # language=HTML
    template: types.django_html = """
        <div class="wavy-seperator-top">
            <div class="content">
                {% slot "content" default / %}
            </div>
            <div class="wave-top"></div>
        </div>
    """
    # language=CSS
    css: types.css = """
    
        .wave-top {
            position: relative;
            top: 0;
            z-index: 10;
            top: -1px;
            background-image: url('/media/wave3.svg');
            background-position: top center;
            background-size: cover; 
            background-repeat: no-repeat;
            height: 5vh;
            width: 100%;
        }

        .content {
            background-color: var(--background-blue);
        }
    """

    # language=JS
    js: types.js = """

    """
