from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Article, Author
from django.urls import reverse_lazy, reverse
from .forms import AuthorCreateForm, ArticleForm


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'
    queryset = (Article.objects.select_related('author', 'category')
                .prefetch_related('tags').defer('content').filter(pub_date__isnull=False))


class ArticleCreateView(CreateView):
    model = Article
    fields = ['title', 'content', 'pub_date', 'author', 'category', 'tags']
    template_name = 'blogapp/create_article.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blogapp/article_details.html'


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blogapp/article_update_form.html'
    success_url = reverse_lazy('blogapp:articles')


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'blogapp/article_delete_confirm.html'
    success_url = reverse_lazy('blogapp:articles')


# Get the User model
User = get_user_model()


class CreateUserView(CreateView):
    template_name = 'blogapp/register.html'
    form_class = AuthorCreateForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # the form_valid function is called when a form is deemed to be valid,
        # i.e all form fields have passed validation.
        # Here, we are overriding the form_valid function to perform additional actions.
        # After saving the form data to create the user, we are storing user's bio and creating an Author instance
        # associated with the user.
        user = form.save()
        bio = form.cleaned_data.get('bio')
        Author.objects.create(user=user, bio=bio)
        return super().form_valid(form)


class LatestArticlesFeed(Feed):
    title = "Latest Articles"
    link = "blogapp:articles"
    description = "Updates on the latest articles"

    def items(self):
        return Article.objects.filter(pub_date__isnull=False).order_by('-pub_date')[:5]

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    def item_link(self, item):
        return reverse('blogapp:article_details', args=[item.pk])
