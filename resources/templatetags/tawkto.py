"""Template tags to implement tawk.to on a website."""
from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


@register.simple_tag()
def tawkto():
    """
    Return script for include tawk.to.

    Usage:
    ```
    {% load tawkto %}
    {% tawkto %}
    ```
    """
    if not settings.TAWKTO_ID:
        return ""

    return format_html(
        """
<!--Start of Tawk.to Script-->
<script type="text/javascript">
var Tawk_API=Tawk_API||{{}}, Tawk_LoadStart=new Date();
(function(){{
var s1=document.createElement("script"),s0=document.getElementsByTagName("script")[0];
s1.async=true;
s1.src='https://embed.tawk.to/{}/default';
s1.charset='UTF-8';
s1.setAttribute('crossorigin','*');
s0.parentNode.insertBefore(s1,s0);
}})();
</script>
<!--End of Tawk.to Script-->
""",
        settings.TAWKTO_ID,
    )
