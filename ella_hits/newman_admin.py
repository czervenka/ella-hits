import ella_newman
from django.utils.safestring import mark_safe
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _


class HitCountAdmin(ella_newman.NewmanModelAdmin):
    list_display = ('target', 'hits', 'publish_from', 'target_url')
    raw_id_fields = ('publishable',)
    search_fields = ('publishable__category__title', 'publishable__pk', 'publishable__title', 'publishable__slug' )
    ordering = ('-hits', '-last_seen',)

    def publish_from(self, object):
        return object.publishable.publish_from

    publish_from.short_description = _('Publish from')
    publish_from.allow_tags = True
    publish_from.order_field = 'publish_from'

    def target_url(self, object):
        target = object.target()
        return mark_safe('<a class="icn web" href="%s">%s</a>' % (target.get_absolute_url(), target))
    target_url.short_description = _('View on site')
    target_url.allow_tags = True

    def get_urls(self):

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^by-category/$',
                self.by_category_view,
                name='%sadmin_%s_%s_by_category' % info),
        )
        urlpatterns += super(HitCountAdmin, self).get_urls()
        return urlpatterns

    def by_category_view(self, request, extra_context={}):
        pass
