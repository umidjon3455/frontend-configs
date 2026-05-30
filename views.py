from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView

from accounts.models import Profile
from config.custom_permissions import OnlyLoggedSuperUser
from .forms import ContactForm, CommentForm
from .models import Category, News
from django.http import Http404, HttpResponse
from django.db.models import Q
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin


# Create your views here.

def news_list(request):
    news_list = News.objects.filter(status=News.Status.Published)

    context = {'news_list': news_list}

    return render(request, "news/news_list.html", context=context)


# def news_detail(request, news):
#     news = get_object_or_404(News, slug=news, status=News.Status.Published)
#     recomend_news = News.published.all().order_by('-publish_time')[:6]
#     context = {'news': news,
#                'recomend_news': recomend_news}
#     return render(request, "news/single.html", context)


from django.views.generic import TemplateView
from .models import News, Category


class HomePageView(TemplateView):
    template_name = 'news/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 🔥 DEBUG (terminalda ko‘rish uchun)
        user = self.request.user
        print("USER:", user)

        if user.is_authenticated:
            print("USERNAME:", user.username)
        else:
            print("User login qilmagan")

        # 🔹 Query optimizatsiya
        qs = News.published.all()

        context['categories'] = Category.objects.all()
        context['news_list'] = qs.order_by('-publish_time')[:4]
        context['local_news'] = qs.filter(category__name="Uzbekistan").order_by('-publish_time')
        context['world_news'] = qs.filter(category__name="Jahon").order_by('-publish_time')[:4]
        context['sport_news'] = qs.filter(category__name="Sport").order_by("-publish_time")
        context['techno_news'] = qs.filter(category__name="Fan_texnika").order_by("-publish_time")
        context['economy'] = qs.filter(category__name="Iqtisodiyot").order_by("-publish_time")
        context['jamiyat'] = qs.filter(category__name="Jamiyat").order_by("-publish_time")

        return context



class LocalNewsView(ListView):
    model = News
    template_name = 'news/local.html'
    context_object_name = 'localnews'

    def get_queryset(self, **kwargs):
        news = News.published.all().filter(category__name="Uzbekistan").order_by('-publish_time')

        return news


class WorldNewsView(ListView):
    model = News
    template_name = 'news/jahon.html'
    context_object_name = 'worldnews'

    def get_queryset(self, **kwargs):
        news = News.published.all().filter(category__name="Jahon").order_by('-publish_time')

        return news


class SubjectNewsView(ListView):
    model = News
    template_name = 'news/fan_texnika.html'
    context_object_name = 'fannews'

    def get_queryset(self, **kwargs):
        news = News.published.all().filter(category__name="Fan_texnika").order_by("-publish_time")

        return news


class SportNewsView(ListView):
    model = News
    template_name = 'news/Sport.html'
    context_object_name = 'sportnews'

    def get_queryset(self, **kwargs):
        news = News.published.all().filter(category__name="Sport").order_by("-publish_time")

        return news


class IqtisodiyotNewsView(ListView):
    model = News
    template_name = 'news/Iqtisodiyot.html'
    context_object_name = 'iqtisodiyotnews'

    def get_queryset(self, **kwargs):
        news = News.published.all().filter(category__name="Iqtisodiyot").order_by("-publish_time")

        return news


class ContactPageView(TemplateView):
    templates_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            'form': form
        }
        return render(request, "news/contact.html", context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponse("<h2> Ok  <h2>")
        context = {
            'form': form
        }
        return render(request, 'news/contact.html', context)


# def single(request):
#     data = News.objects.filter(status=News.Status.Published)
#     category = Category.objects.all()
#
#     context = {
#         "data": data,
#         "category": category
#     }
#
#     return render(request, 'news/single.html', context)


class NewsUpdtaeView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status',)
    template_name = 'crud/news_edit.html'
    success_url = reverse_lazy('homepage')


class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('homepage')


class NewsCreateView(OnlyLoggedSuperUser, CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = (
        'title', 'title_uz', 'title_en', 'title_ru', 'slug', 'body', 'body_uz', 'body_en', 'body_ru', 'image',
        'category',
        'status',)
    success_url = reverse_lazy('homepage')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_page(request):
    admin_users = User.objects.filter(is_superuser=True)
    users = User.objects.all()

    context = {
        "admin_users": admin_users,
        'users':users
    }
    return render(request, 'pages/admin_page.html', context)


def news_detail(request, news):
    recomend_news = News.published.all().order_by('-publish_time')
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    context = {}
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hit_count'] = {'pk': hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext['hit_counted'] = hit_count_response.hit_counted
        hitcontext['hit_message'] = hit_count_response.hit_message
        hitcontext['total_hits'] = hits

    comments = news.comments.filter(active=True)
    comments_count = comments.count()
    comments_count = comments_count + 1

    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            # izoh egasi sorov yuborgan user
            new_comment.user = request.user
            # db saqlimiz
            new_comment.save()
            # izoh textni tozalash
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        'recomend_news': recomend_news,
        "news": news,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'comments_count': comments_count,

    }

    return render(request, 'news/single.html', context)


# class SearchResultsList(ListView):
#     model = News
#     template_name = 'news/search_results.html'
#     context_object_name = 'all_news'
#
#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         return News.objects.filter(
#             Q(title__icontains=query) | Q(body__icontains=query)
#         )


def search_view(request):
    query = request.GET.get('q')  # Получаем строку запроса из GET параметра 'q'
    results = News.objects.filter(title__icontains=query) or News.objects.filter(
        body__icontains=query)  # Ищем объекты, удовлетворяющие запросу

    if not results:
        # Если результаты не найдены, то делаем что-то, например, выводим сообщение об отсутствии результатов
        return render(request, 'news/no_results.html', {'query': query})
    else:
        # Если результаты найдены, передаем их в шаблон для отображения
        return render(request, 'news/search_results.html', {'all_news': results, 'query': query})


def handler404(request, exception):
    return render(request, 'news/404.html', status=404)
