from django import template
from django.db import models, transaction
from django.template import Variable, VariableDoesNotExist

from ella.core.models import HitCount, Publishable
from ella.core.cache import get_cached_object
from ella.core.conf import core_settings

register = template.Library()


class TopVisitedNode(template.Node):
    def __init__(self, count, name, days=None, mods=None):
        self.count, self.name, self.days, self.mods = count, name, days, mods

    def render(self, context):
        context[self.name] = HitCount.objects.get_top_objects(self.count, self.days, self.mods)
        return ''

@register.tag('top_visited')
def do_top_visited(parser, token):
    """
    Get list of COUNT top visited objects of given model and store them in context under given name.

    Usage::

        {% top_visited 5 [days 30] [app.model ...] as var %}

    Example::

        {% top_visited 10 as top_visited_objects %}
        {% for obj in top_visited_objects %}   ...   {% endfor %}

        {% top_visited 10 days 30 as top_visited_objects %}
        {% for obj in top_visited_objects %}   ...   {% endfor %}

        {% top_visited 10 articles.article as top_articles %}
        {% for article in top_articles %}   ...   {% endfor %}

        {% top_visited 10 days 30 articles.article as top_articles %}
        {% for article in top_articles %}   ...   {% endfor %}

        {% top_visited 10 days 30 articles.article photos.photo as top_objects %}
        {% for obj in top_objects %}   ...   {% endfor %}
    """
    count, result, days, mods = top_visited_parser(token.split_contents())
    return TopVisitedNode(count, result, days, mods)

def top_visited_parser(bits):
    if len(bits) < 4 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "{% top_visited 5 [days 30] [app.model ...] as var %}"

    try:
        count = int(bits[1])
    except ValueError:
        raise template.TemplateSyntaxError, "{% top_visited 5 [days 30] [app.model ...] as var %}"

    if bits[2] == 'days':
        try:
            days = int(bits[3])
            if days < 1:
                raise template.TemplateSyntaxError, "Days argument must be greater then 0"
        except ValueError:
            raise template.TemplateSyntaxError, "{% top_visited 5 [days 30] [app.model ...] as var %}"
        mods_start = 4
    else:
        days = None
        mods_start = 2

    mods = []
    for mod in bits[mods_start:-2]:
        model = models.get_model(*mod.split('.', 1))
        if not model:
            raise template.TemplateSyntaxError, "{% top_visited 5 [days 30] [app.model ...] as var %}"
        mods.append(model)

    return count, bits[-1], days, mods


class HitCountNode(template.Node):
    def __init__(self, publishable, pk, position):
        self.publishable, self.pk = pk, self.position=position

    @transaction.commit_on_success
    def render(self, context):
        if self.pk:
            try:
                publishable = get_cached_object(Publishable, pk=self.publishable)
            except Publishable.DoesNotExist:
                return ''
        else:
            try:
                publishable = Variable(self.publishable).resolve(context)
            except VariableDoesNotExist:
                return ''

        if core_settings.DOUBLE_RENDER and 'SECOND_RENDER' not in context:
            return '{%% load hits %%}{%% hitcount for pk %(place_pk)s %%}' % {
                'place_pk' : publishable.pk,
            }
        HitCount.objects.hit(publishable, self.position)
        return ''

@register.tag
def hitcount(parser, token):
    """
    Increment hit counter via template tag

    Usage::
        {% hitcount for publishable %}
        {% hitcount for pk 12 %}
        {% hitcount for publishable at "sitebar" %}
    """
    bits = token.split_contents()
    pk = False
    if len(bits) >= 3 and bits[1] == 'for':
        publishable = bits[2]
        last_bit = 2
    elif len(bits) >= 4 and bits[1] == 'for' and bits[2] == 'pk':
        publishable = bits[3]
        last_bit = 3
        pk = True
    else:
        raise template.TemplateSyntaxError('{% hitcount for [pk] {publishable|pk} %}')

    if len(bits) == last_bit + 3 and bits[last_bit + 1] == 'at':
        position = bits[last_bit + 2]
    elif len(bits) == last_bit + 1:
        position = None
    else:
        raise template.TemplateSyntaxError('{% hitcount for [pk] {publishable|pk} %}')
        
        
    return HitCountNode(publishable, pk, position)

