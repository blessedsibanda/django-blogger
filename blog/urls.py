from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('articles/popular/', views.PopularArticlesView.as_view(), name='popular_articles'),
    path('articles/create/', views.AddArticleView.as_view(), name='create_article'),
    path('article/<slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<slug>/like/', views.like_article, name='like_article'),
    path('article/<slug>/dislike/', views.dislike_article, name='dislike_article'),
    path('article/<slug>/update/', views.UpdateArticleView.as_view(), name='article_update'),
    path('user/<username>/', views.UserPageView.as_view(), name='user_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/<int:pk>/update', views.EditProfileView.as_view(), name='profile_update'),
]