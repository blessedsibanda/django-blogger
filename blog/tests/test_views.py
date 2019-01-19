from django.test import TestCase, tag
from django.urls import reverse
from mixer.backend.django import mixer

from blog.models import Article, Profile 


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


class AddArticleView(TestCase):
    def test_unauthenticated_user(self):
        """
        Unauthenticated users cannot create articles so they are
        redirected to the login page first.
        """
        response = self.client.get(reverse('create_article'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user(self):
        """
        Authenticated users can create articles.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        response = self.client.get(reverse('create_article'))
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        """
        A valid form submitted results in a new article.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        data = {
            "title": "New Article",
            "content": "Fresh content"
        }
        url = reverse('create_article')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # successful post request returns a redirect
        self.assertEqual(Article.objects.count(), 1)

    def test_invalid_data(self):
        """
        An invalid form does not create a new article.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        data = {
            "title": "New Article",
        }
        url = reverse('create_article')
        response = self.client.post(url, data)
        self.assertNotEqual(response.status_code, 302)  # unsuccessful post request returns same page
        self.assertEqual(Article.objects.count(), 0)


class EditProfileViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = mixer.blend('auth.User')
        cls.url = reverse('profile_update', args=(cls.user.profile.pk,))


    def test_authenticated_user(self):
        """
        Authenticated users can edit their profiles.
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_update_profile(self):
        self.client.force_login(self.user)
        old_profile = self.user.profile
        data = {
            'user': self.user,
            'full_name': 'Test User',
        }
        response = self.client.post(self.url, data)
        new_profile = Profile.objects.get(user=self.user)
      
        self.assertNotEqual(old_profile.full_name, new_profile.full_name)
        self.assertEqual(response.status_code, 302)
    

class UpdateArticleViewTests(TestCase):
    def test_article_updates(self):
        article = mixer.blend('blog.article')
        url = reverse('article_update', args=(article.slug,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = {
            'title': 'Updated title',
            'content': 'Updated content'
        }
        original_article = article
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        updated_article = Article.objects.get(pk=1)
        self.assertNotEqual(original_article.title, updated_article.title)
        self.assertEqual(updated_article.title, 'Updated title')
        self.assertEqual(updated_article.content, 'Updated content')


class UserPageViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = mixer.blend('auth.User')
        cls.url = reverse('user_page', args=(cls.user.username,))

    def test_page_works(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/user_page.html')

    def test_page_raises_404_for_non_existent_username(self):
        self.url = reverse('user_page', args=('unknown',))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_page_works_and_returns_user_articles(self):
        """
        The `user_page` returns all the user articles.
        """
        response = self.client.get(self.url)
        self.assertQuerysetEqual(
            response.context['user_articles'],
            self.user.article_set.filter(publish=True)
        )


class LikeDislikeViewsTests(TestCase):
    def test_like_article_by_unauthenticated_user(self):
        """
        Uauthenticated users are redirected to the `login` page before they
        can like an article.
        """
        article = mixer.blend('blog.article', publish=True)
        url = reverse('like_article', args=(article.slug, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.like_set.count(), 0)

    def test_like_article_by_authenticated_user(self):
        """
        Authenticated users can like articles.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        article = mixer.blend('blog.article', publish=True)
        url = reverse('like_article', args=(article.slug, ))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.like_set.count(), 1)

    @tag('b')
    def test_like_article_on_liked_article_by_authenticated_user(self):
        """
        An article can only be liked once by the same user.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        article = mixer.blend('blog.article', publish=True)
        url = reverse('like_article', args=(article.slug, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.like_set.count(), 1) 
        url = reverse('like_article', args=(article.slug, ))

        # second like action
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(article.like_set.count(), 1) # likes count still at 1 not 2
         

    def test_dislike_article_by_unauthenticated_user(self):
        """
        Uauthenticated users are redirected to the `login` page before they
        can dislike an article.
        """
        article = mixer.blend('blog.article', publish=True)
        url = reverse('dislike_article', args=(article.slug, ))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.dislike_set.count(), 0)

    def test_dislike_article_by_authenticated_user(self):
        """
        Aauthenticated users can dislike articles.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        article = mixer.blend('blog.article', publish=True)
        url = reverse('dislike_article', args=(article.slug, ))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(article.dislike_set.count(), 1)

    def test_dislike_article_on_liked_article_by_authenticated_user(self):
        """
        An article can only be disliked once by the same user.
        """
        user = mixer.blend('auth.User')
        self.client.force_login(user)
        article = mixer.blend('blog.article', publish=True)
        url = reverse('dislike_article', args=(article.slug, ))
        response = self.client.get(url)
        #self.assertEqual(response.status_code, 302)
        self.assertEqual(article.dislike_set.count(), 1)  

        # second dislike action
        response = self.client.get(url)
        #self.assertEqual(response.status_code, 200)
        self.assertEqual(article.dislike_set.count(), 1) # dislikes still 1 not 2