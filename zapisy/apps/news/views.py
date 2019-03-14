import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render, redirect

from apps.news.models import News
from apps.users.models import BaseUser


def all_news(request):
    """
        Latest news, result of query search or given page with focused news
    """
    if BaseUser.is_student(request.user):
        student = request.user.student
        student.last_news_view = datetime.datetime.now()
        student.save()

    elif BaseUser.is_employee(request.user):
        employee = request.user.employee
        employee.last_news_view = datetime.datetime.now()
        employee.save()

    query = request.GET.get('q')
    if query:
        query = query.strip()
        items = News.objects.get_published().filter(Q(title__icontains=query) | Q(body__icontains=query))
    else:
        items = News.objects.exclude(category='-')

    paginator = Paginator(items, settings.NEWS_PER_PAGE)
    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        news = paginator.page(1)

    data = {'items': news, 'page_range': paginator.page_range, 'query': query}

    return render(request, 'news/list_all.html', data)


def all_news_focus_one(request, news_id):
    """
      Return page with focus on element with news_id (default: all_news)
    """
    page = News.objects.get_page_number_by_news_id(int(news_id))
    return redirect('{0}?page={1}#od-news-{2}'.format(reverse('news-all'), page, news_id))


def main_page(request):
    all_news_except_hidden = News.objects.exclude(category='-') \
        .order_by("-date").select_related('author')
    recent_news = all_news_except_hidden[:2] if all_news_except_hidden else None
    return render(request, 'common/index.html', {'recent_news': recent_news})
