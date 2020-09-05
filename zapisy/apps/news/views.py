import urllib.parse

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import News


def all_news(request):
    """Latest news, result of query search or given page with focused news."""
    query = request.GET.get('q')
    if query:
        query = query.strip()
        items = News.objects.published().filter(
            Q(title__icontains=query) | Q(body__icontains=query))
    else:
        items = News.objects.published()

    paginator = Paginator(items, settings.NEWS_PER_PAGE)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        news = paginator.page(1)

    # Allows to combine query with pagination.
    self_url = '?'
    if query:
        self_url += f'q={urllib.parse.quote_plus(query)}&'

    return render(request, 'news/list_all.html', {
        'items': news,
        'page_range': paginator.page_range,
        'query': query,
        'self_url': self_url
    })


def all_news_focus_one(request, news_id):
    """Return page with focus on element with news_id (default: all_news)."""
    page = News.objects.get_page_number_by_news_id(int(news_id))
    return redirect('{0}?page={1}#od-news-{2}'.format(reverse('news-all'), page, news_id))


def main_page(request):
    all_news_except_hidden = News.objects.published().select_related('author')
    recent_news = all_news_except_hidden[:2] if all_news_except_hidden else None
    return render(request, 'common/index.html', {'recent_news': recent_news})
