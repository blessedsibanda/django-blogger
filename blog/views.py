from operator import attrgetter

from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.urls import reverse_lazy
from django.views import generic 
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Article, Profile, Like, Dislike


class ArticleListView(generic.ListView):
    queryset = Article.published.all()
    paginate_by = 5
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = {}
        if self.request.GET.get('query', None):
            query = self.request.GET['query'].strip()
            if query:
                keywords = query.split()
                q = Q()
                for keyword in keywords:
                    q = q & Q(title__icontains=keyword)
                if len(query) > 0:
                    context['query'] = query
                context['articles'] = Article.published.filter(q)[:10] 
        self.request.authors = User.objects.all()
        context.update(kwargs)  
        return super().get_context_data(**context)


class ArticleDetailView(generic.DetailView):
    model = Article

    def get_context_data(self, ** kwargs):
        context = super().get_context_data( ** kwargs)
        context['user'] = self.object.author
        return context

    def get_queryset(self):
        return Article.published.all()

class DashboardView(generic.TemplateView):
    template_name = 'blog/dashboard.html'
    extra_context = {}

    @method_decorator(login_required)
    def dispatch(self, * args, ** kwargs):
        user = self.request.user 
        self.extra_context['user'] = user
        return super().dispatch( * args, ** kwargs)


class AddArticleView(generic.CreateView):
    model = Article
    #template_name = 'blog/article_form.html'
    success_url = '/'
    fields = ['title', 'content', 'publish']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, * args, ** kwargs):
        return super().dispatch( * args, ** kwargs)


class EditProfileView(generic.UpdateView):
    model = Profile
    fields = ['full_name','bio','avatar','github','facebook','twitter']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.avatar = form.instance.avatar
        return super().form_valid(form)


class UpdateArticleView(generic.UpdateView):
    model = Article
    success_url = reverse_lazy('dashboard')
    fields = ['title', 'content', 'publish']

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)

class UserPageView(generic.TemplateView):
    template_name = 'blog/user_page.html'

    def get_context_data(self, **kwargs):
        context = {}
        username = kwargs['username']
        user = get_object_or_404(User,username=username)
        context['user'] = user
        context['user_articles'] = Article.published.filter(author=user)
        context['article_count'] = Article.published.filter(author=user).count()
        context.update(kwargs)  
        return super().get_context_data(**context)

@login_required
def like_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user
    print(request.method)
    likes = Like.objects.filter(user=user).filter(article=article)
    print(likes)
    if len(likes) > 0:
        print('like not created')
        return render(request, 'blog/article_detail.html', {'article': article})
    print('like created')
    Like.objects.create(article=article, user=user)
    return redirect(article.get_absolute_url())
    

@login_required
def dislike_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user
    dislikes = Dislike.objects.filter(user=user).filter(article=article)
    if len(dislikes) > 0:
        return render(request, 'blog/article_detail.html', {'article': article})
    Dislike.objects.create(article=article, user=user)
    return redirect(article.get_absolute_url())


class PopularArticlesView(generic.ListView):
    queryset = Article.published.all()
    # popular articles should have at least a single like
    queryset = [article for article in queryset if article.likes > 0] 
    queryset = sorted(queryset, key=attrgetter('popularity_score'))[:10]
    context_object_name = 'articles'
    template_name = 'blog/article_list.html'
    paginate_by = 5    # Show 5 articles per page