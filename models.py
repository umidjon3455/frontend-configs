# from django.contrib.auth.models import User
# from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class Blog(models.Model):
#     title = models.CharField(max_length=100)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     text = models.TextField()
#
#     def __str__(self):
#         return self.title


from django.db import models
from django.utils import timezone
from django.urls import reverse


# Create your models here.


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=News.Status.Published)


class Video(models.Model):
    title = models.CharField(max_length=100)
    mp4_file = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        Published = 'PB', 'Published'

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300)
    body = models.TextField()
    image = models.ImageField(upload_to='news/images', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publish_time = models.DateTimeField(default=timezone.now)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-publish_time"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news_detail_page", args=[self.slug])


class ContactData(models.Model):
    adress = models.CharField(max_length=150)
    phone = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.adress


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=150)
    message = models.TextField()

    def __str__(self):
        return self.email


class Comment(models.Model):
    news = models.ForeignKey(News,
                             on_delete=models.CASCADE,
                             related_name='comments')

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments')

    body = models.TextField(max_length=300)
    created_time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_time']

    def __str__(self):
        return f"Comment = {self.body} by {self.user}"
