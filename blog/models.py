from django.utils import timezone
from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.http import HttpRequest

class PublishedArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publish=True)

class Article(models.Model):
    title = models.CharField(unique=True, max_length=120)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()
    publish = models.BooleanField(default=False)
    pub_date = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField()

    objects = models.Manager()
    published = PublishedArticleManager()

    def __str__(self):
        return f'{self.title} by {self.author.username}'

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.publish:
            if not self.pub_date:
                self.pub_date = timezone.now()
        else: 
            self.pub_date = None
        super(Article, self).save(*args, **kwargs)

    @property
    def likes(self):
        return self.like_set.count()

    @property
    def dislikes(self):
        return self.dislike_set.count()

    @property
    def popularity_score(self):
        return self.dislikes - self.likes    # the higher the score, the less popular the article

    class Meta:
        ordering = ('-pub_date',)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images/avatars', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=30)
    github = models.URLField(blank=True, null=True)
    twitter = models.CharField(blank=True, null=True, max_length=50)
    website = models.URLField(blank=True, null=True)
    facebook = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f'Profile, {self.user.username}'


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.ForeignKey)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'article'),)


class Dislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.ForeignKey)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'article'),)

    
