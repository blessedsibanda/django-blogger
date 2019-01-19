from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

import pprint


class ArticleListViewTests(TestCase):
    def test_no_articles(self):
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_list.html')
        self.assertContains(response, 'No articles available yet.')

    def test_three_published_and_two_unpublished_articles(self):
        """
        The `ArticleListView only displays published articles.
        """
        pub_article1 = mixer.blend('blog.article', title='Published Article 1', publish=True)
        unpub_article1 = mixer.blend('blog.article', title='Unpublished Article 1')
        pub_article2 = mixer.blend('blog.article', title='Published Article 2', publish=True)
        unpub_article2 = mixer.blend('blog.article', title='Unpublished Article 2')
        pub_article3 = mixer.blend('blog.article', title='Published Article 3', publish=True)
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['articles']),
            3
        )

    def test_search_if_query_exists(self):
        query = 'python'
        article1 = mixer.blend('blog.article', title='Web dev with Python', publish=True)
        article2 = mixer.blend('blog.article', title='Javascript for beginners', publish=True)
        article3 = mixer.blend('blog.article', title='Build a web app with python and django', publish=True)
        response = self.client.get(reverse('article_list') + '?query=' + query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['articles']),
            2
        )        


class ArticleDetailViewTests(TestCase):
    def test_unpublished_article(self):
        """
        HTTP 404 Not Found is raised when a detail page for an 
        unpublished article is requested.
        """
        article = mixer.blend('blog.article')
        url = reverse('article_detail', args=(article.slug, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_published_article(self):
        """
        Article details are displayed when a detail page of a
        published article is requested.
        """
        article = mixer.blend('blog.article', publish=True)
        url = reverse('article_detail', args=(article.slug, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertTemplateUsed(response, 'blog/article_detail.html')

    def test_detail_page_displays_profile_of_article_author(self):
        article = mixer.blend('blog.article', publish=True)
        url = reverse('article_detail', args=(article.slug, ))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'blog/profile.html')


class DashboardViewTests(TestCase):
    def test_dashboard_page_for_unauthenticated_user(self):
        """
        Unauthenticated users cannot have access to dashboard page.
        """
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)
        # unauthenticated users are redirected to the login page
        self.assertEqual(response.status_code, 302)   

    def test_dashboard_page_for_authenticated_user(self):
        """
        Authenticated users access their dashboard page.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)   
        self.assertTemplateUsed(response, 'blog/dashboard.html')
        
    def test_dashboard_page_displays_all_user_articles(self):
        """
        Authenticated users can view all their articles (both published and 
        unpublished) in their dashboard page.
        """
        user = mixer.blend('auth.User')

        article1 = mixer.blend('blog.article', author=user)
        article2 = mixer.blend('blog.article', author=user, publish=True)
        article3 = mixer.blend('blog.article', author=user)
        article4 = mixer.blend('blog.article', author=user, publish=True)
        article5 = mixer.blend('blog.article', author=user, publish=True)

        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, article1.title)
        self.assertContains(response, article2.title)
        self.assertContains(response, article3.title)
        self.assertContains(response, article4.title)
        self.assertContains(response, article5.title)

    def test_dashboard_displays_user_profile(self):
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'blog/profile.html')