from django.test import TestCase
from django.contrib.auth.models import User 
from mixer.backend.django import mixer 
from django.db.transaction import TransactionManagementError

from blog.models import Like, Article

class ArticleModelTests(TestCase):
    def test_published_article_model_manager(self):
        published_article = mixer.blend('blog.article', publish=True)
        unpublished_article = mixer.blend('blog.article')
        published_articles = Article.published.count()
        self.assertEqual(published_articles, 1)

    def test_published_article_model_manager_with_no_published_articles(self):
        article1 = mixer.blend('blog.article')
        article2 = mixer.blend('blog.article')
        published_articles = Article.published.count()
        self.assertEqual(published_articles, 0)

    def test_save_method_with_no_publish(self):
        """
        If the article is not published, the pub_date is None
        """
        article = mixer.blend('blog.article')
        self.assertEqual(article.pub_date, None)

    def test_save_method_with_publish(self):
        """
        If the article is published, the pub_date is not None
        """
        article = mixer.blend('blog.article', publish=True)
        self.assertNotEqual(article.pub_date, None)

    def test_model_likes_property(self):
        article = mixer.blend('blog.article', publish=True)
        user = mixer.blend('auth.User')
        mixer.blend('blog.like', user=user, article=article)
        self.assertEqual(article.likes, 1)

    def test_model_dislikes_property(self):
        article = mixer.blend('blog.article', publish=True)
        user = mixer.blend('auth.User')
        mixer.blend('blog.dislike', user=user, article=article)
        self.assertEqual(article.dislikes, 1)

    def test_model_popularity_score_property(self):
        """
            `popularity_score = dislikes - likes`
        """
        article = mixer.blend('blog.article', publish=True)
        user1 = mixer.blend('auth.User')
        user2 = mixer.blend('auth.User')
        mixer.blend('blog.like', user=user1, article=article)
        mixer.blend('blog.like', user=user2, article=article)
        mixer.blend('blog.dislike', user=user1, article=article)
        self.assertEqual(article.popularity_score, -1)


class LikeModelTests(TestCase):
    def test_unique_constraint_for_different_users_on_same_article(self):
        user1 = mixer.blend('auth.User')
        user2 = mixer.blend('auth.User')
        article = mixer.blend('blog.Article')
        mixer.blend('blog.like', user=user1, article=article)
        mixer.blend('blog.like', user=user2, article=article)
        total_likes = Like.objects.count()
        self.assertEqual(total_likes, 2)

    def test_unique_constraint_for_single_user_on_different_articles(self):
        user = mixer.blend('auth.User')
        article1 = mixer.blend('blog.Article')
        article2 = mixer.blend('blog.Article')
        mixer.blend('blog.like', user=user, article=article1)
        mixer.blend('blog.like', user=user, article=article2)
        total_likes = Like.objects.count()
        self.assertEqual(total_likes, 2)

