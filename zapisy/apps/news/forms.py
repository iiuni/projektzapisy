from django.forms import ModelForm

from apps.news.models import News


class NewsForm(ModelForm):
    """
        Form for news
    """

    class Meta:
        model = News
        fields = ('title', 'body')


class NewsAllForm(ModelForm):
    """
        Form for news
    """

    class Meta:
        model = News
        fields = ('title', 'category', 'body')
