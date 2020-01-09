from django.contrib import admin
from django.utils.html import format_html

from .models import User, Prediction, PredictionBK, Link


class PredictionBKInlineAdmin(admin.TabularInline):
    model = PredictionBK
    extra = 0


class PredictionAdmin(admin.ModelAdmin):
    list_display = ['link', 'user', 'date', 'sport', 'league', 'teams', 'prediction', 'match_result', 'prediction_result', 'prediction_url']
    list_editable = ['prediction_result', 'match_result']
    ordering = ('-date',)
    inlines = [PredictionBKInlineAdmin]

    def prediction_url(self, obj):
        return format_html('<a href="%s">%s</a>' % (obj.link_to_odd, obj.link_to_odd))

    prediction_url.allow_tags = True


class LinkAdmin(admin.ModelAdmin):
    list_display = ['link', 'password', 'won', 'lose', 'bank', 'current_bank']
    list_display_links = ['link', 'password']


admin.site.register(User)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(Link, LinkAdmin)
