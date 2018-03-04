from django.contrib import admin
from django import forms

from apps.news.models import News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        widgets = {
            'body': forms.Textarea(attrs={'class': 'tinymce'})
        }
        fields = '__all__'

class NewsAdmin(admin.ModelAdmin):
    """
        News admin manager
    """
    fields = ('title', 'body', 'author', 'category')
    list_display = ('title', 'date')
    list_filter = ['date']
    form = NewsForm

    class Media:
        js = ('/static/js/tinymce/tinymce.min.js',
              '/static/js/textareas.js',)


admin.site.register(News, NewsAdmin)
