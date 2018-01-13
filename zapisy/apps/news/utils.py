# -*- coding: utf-8 -*-
"""
Various utils.
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import Context, RequestContext
from django.template.loader import get_template
from mailer import send_html_mail

from apps.news.models import News
from apps.users.models import Employee, Student

CATEGORIES = {
    '-': 'Ukryte',
    'offer': 'Oferta',
    'enrollment': 'Zapisy',
    'grade': 'Ocena',
}

MASS_MAIL_FROM = 'noreply@example.com'
NEWS_PER_PAGE = 5


def render_with_device_detection(request, full_tpl, mobi_tpl):
    """ Detects type of device and renders appropriate template"""

    template = full_tpl
    # if request.is_mobile:
    if request.mobile:
        template = mobi_tpl

    return render(request, template)


def render_with_category_template(temp, context):
    """ Switch beetween top menus based on context['category'].

    Changes base ExtendsNode when needed."""
    temp = get_template(temp)
    if context.get('category', '') == 'enrollment':
        temp.nodelist[0].parent_name = 'enrollment/base.html'
    elif context.get('category', '') == 'grade':
        temp.nodelist[0].parent_name = 'grade/base.html'
    elif context.get('category', '') == 'offer':
        temp.nodelist[0].parent_name = 'offer/base.html'
    return HttpResponse(temp.render(context))


def render_items(request, items):
    """
        Renders items
    """
    for item in items:
        item.category = CATEGORIES[item.category]
    con = RequestContext(request, {
        'object_list': items,
    })
    tem = get_template('news/ajax_list.html')
    return tem.render(con)


def render_newer_group(category, beginwith, quantity):
    """
        Renders newer group
    """
    con = Context({
        'category': category,
        'newer_no': quantity,
        'newer_beginwith': beginwith,
    })
    tem = get_template('news/newer_group.html')
    return tem.render(con)


def render_older_group(category, beginwith, quantity):
    """
        Renders older group
    """
    con = Context({
        'category': category,
        'older_no': quantity,
        'older_beginwith': beginwith,
    })
    tem = get_template('news/older_group.html')
    return tem.render(con)


def prepare_data(request, items,
                 beginwith=0, quantity=NEWS_PER_PAGE,
                 archive_view=False, category=None):
    """
        Prepares data
    """
    news_count = News.objects.category(category).count()
    data = {}
    data['category'] = category
    data['content'] = render_items(request, items)
    data['older_group'] = render_older_group(category,
                                             beginwith + quantity,
                                             max(news_count - (beginwith + quantity), 0))
    data['newer_group'] = render_newer_group(category,
                                             max(beginwith - quantity, 0),
                                             beginwith)
    data['archive_view'] = archive_view
    data['search_view'] = False
    return data


def prepare_data_all(request, items,
                     beginwith=0, quantity=NEWS_PER_PAGE,
                     archive_view=False, category=None):
    """
        Prepares data
    """
    data = {}
    data['content'] = render_items(request, items)
    data['search_view'] = False
    return data


def render_search_newer_group(category, page, query):
    """
        Renders search result
    """
    con = Context({
        'category': category,
        'page': page,
        'query': query,
    })
    tem = get_template('news/search_newer_group.html')
    return tem.render(con)


def render_search_older_group(category, page, query):
    """
        Renders search result
    """
    con = Context({
        'category': category,
        'page': page,
        'query': query,
    })
    tem = get_template('news/search_older_group.html')
    return tem.render(con)


def get_search_results_data(request, category=None):
    """
        Gets search result
    """
    try:
        page_n = request.GET.get('page', 1)
        sqs = SearchQuerySet().filter(category=category).order_by('-date')
        form = SearchForm(request.GET, searchqueryset=sqs,
                          load_all=False)
        data = {}
        data['category'] = category
        if 'q' in request.GET and request.GET['q'] and form.is_valid():
            query = form.cleaned_data['q']
            results = map(lambda r: r.object, form.search())
            paginator = Paginator(results, NEWS_PER_PAGE)
            page = paginator.page(page_n)
            data['content'] = render_items(request, page.object_list)
            data['newer_group'] = render_search_newer_group(category, page, query)
            data['older_group'] = render_search_older_group(category, page, query)
            data['archive_view'] = False
            data['search_view'] = True
            return data
        else:
            msg = "Niewłaściwe zapytanie"
            data = {'message': msg}
            return data
    except InvalidPage:
        raise Http404


def render_email_from_news(news):
    """
    Creates multipart email message given a news instance.

    Returns (course, text_body, html_body) triple.
    """
    con = Context({
        'news': news,
        'news_url': "http://" +
        str(Site.objects.get_current().domain) +
        reverse('news-item', args=[news.id])
    })
    tem = get_template('news/email_plaintext.html')
    plaintext_body = tem.render(con)
    tem = get_template('news/email_html.html')
    html_body = tem.render(con)
    from_email = MASS_MAIL_FROM
    course = settings.EMAIL_COURSE_PREFIX + news.title
    return (course, plaintext_body, html_body)


def send_mass_mail(msg_parts, users):
    """
    Queue mass mail to the specified apps.users.
    """
    (course, text_body, html_body) = msg_parts
    emails = set([user.user.email for user in users])
    for email in emails:
        if email:
            send_html_mail(course, text_body, html_body,
                           MASS_MAIL_FROM, [email])


def mail_news_enrollment(news):
    """
    Queue news in form of a mail message to all users
    that haven't opted out.
    """
    users = list(Student.objects.filter(receive_mass_mail_enrollment=True).select_related())
    users += list(Employee.objects.filter(receive_mass_mail_enrollment=True).select_related())
    send_mass_mail(render_email_from_news(news), users)


def mail_news_offer(news):
    """
    Queue news in form of a mail message to all users
    that haven't opted out.
    """
    users = list(Student.objects.filter(receive_mass_mail_offer=True).select_related())
    users += list(Employee.objects.filter(receive_mass_mail_offer=True).select_related())
    send_mass_mail(render_email_from_news(news), users)


def mail_news_grade(news):
    """
    Queue news in form of a mail message to all users
    that haven't opted out.
    """
    users = list(Student.objects.filter(receive_mass_mail_grade=True).select_related())
    users += list(Employee.objects.filter(receive_mass_mail_grade=True).select_related())
    send_mass_mail(render_email_from_news(news), users)
