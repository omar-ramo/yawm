import bleach
from django.db import models
from django.db.models import Count, F, Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
from django.utils.html import strip_tags
from ckeditor_uploader.fields import RichTextUploadingField
from notifications.models import Notification
from notifications.signals import notify

from accounts.models import Profile
from core.utils import get_image_upload_path, generate_random_string
from .utils import delete_ckeditor_rich_text_images


class DiaryQuerySet(models.QuerySet):

    def active(self, user):
        if not user.is_authenticated:
            qs = self.filter(is_visible=Diary.ALL_CHOICE)
        else:
            # User can see his non-visible diaries.
            qs = self.filter(
                Q(author=user.profile) |
                Q(is_visible=Diary.ALL_CHOICE))
            qs = qs.distinct()
        qs = qs.select_related('author')
        return qs

    def from_followed_profiles(self, profile):
        followed_profiles = profile.followed_profiles.all()
        qs = self.filter(author__in=followed_profiles)
        return qs

    def popular(self):
        qs = self.annotate(
            ranking_factor=F('comments_count') + F('likes_count')
        )
        qs = qs.order_by('-ranking_factor')
        return qs


class Diary(models.Model):
    ALL_CHOICE = 'all'
    NO_ONE_CHOICE = 'no_one'
    VISIBILITY_CHOICES = (
        (ALL_CHOICE, 'All'),
        (NO_ONE_CHOICE, 'No One'))
    COMMENTABLE_CHOICES = (
        (ALL_CHOICE, 'All'),
        (NO_ONE_CHOICE, 'No One'))
    ANGRY_FEELING = '0'
    HAPPY_FEELING = '1'
    EXCITED_FEELING = '2'
    SAD_FEELING = '3'
    LOVE_FEELING = 'LOVE'
    SATISFIED_FEELING = 'SATISFIED'
    MAD_FEELING = 'MAD'
    TIRED_FEELING = 'TIRED'
    SURPRISED_FEELING = 'SURPRISED'
    AFRAID_FEELING = 'AFRAID'
    FEELINGS_CHOICES = (
        (ANGRY_FEELING, 'Angry'),
        (HAPPY_FEELING, 'Happy'),
        (EXCITED_FEELING, 'Excited'),
        (SAD_FEELING, 'Sad'),
        (LOVE_FEELING, 'Love'),
        (SATISFIED_FEELING, 'Satisfied'),
        (MAD_FEELING, 'Mad'),
        (TIRED_FEELING, 'Tired'),
        (SURPRISED_FEELING, 'Surprised'),
        (AFRAID_FEELING, 'Afraid'),)

    title = models.CharField(max_length=255)
    # Size of slug is bigger than size of title
    # Because we want to add random string at the end
    slug = models.SlugField(max_length=275, blank=True, allow_unicode=True)
    content = RichTextUploadingField()
    description = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(
        upload_to=get_image_upload_path,
        null=True,
        blank=True)
    is_visible = models.CharField(
        help_text='Who can see this diary?',
        max_length=7,
        choices=VISIBILITY_CHOICES,
        default=ALL_CHOICE)
    is_commentable = models.CharField(
        help_text='Who can comment on this diary?',
        choices=COMMENTABLE_CHOICES,
        max_length=7,
        default=ALL_CHOICE)
    feeling = models.CharField(
        help_text='How do you feel?',
        max_length=15,
        choices=FEELINGS_CHOICES,
        null=True,
        blank=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(
        Profile,
        through='DiaryLike',
        through_fields=('diary', 'user'))
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(
        Profile,
        related_name='written_diaries',
        on_delete=models.CASCADE)

    objects = DiaryQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'diaries'
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if(not self.id):
            new_slug = '{}-{}'.format(
                slugify(self.title, allow_unicode=True),
                generate_random_string())

            while Diary.objects.filter(slug=new_slug).exists():
                new_slug = '{}-{}'.format(
                    slugify(self.title, allow_unicode=True),
                    generate_random_string())

            self.slug = new_slug

        # self.description is supposed to be plain text so that it's displayed
        # in the diary list page
        start_position = 500
        end_position = len(self.content)
        plain_text_description = bleach.clean(
            self.content[:start_position],
            strip=True,
            tags=[],
            attributes=[]
        ).strip()
        # If 500 non-clean characters is not enough, add 10 every time
        while len(plain_text_description) < 245 & start_position < end_position:
            plain_text_description +=  bleach.clean(
                self.content[start_position:start_position + 10],
                strip=True,
                tags=[],
                attributes=[]
            ).strip()
            start_position += 10
        self.description = plain_text_description[:255]

        return super(Diary, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'diaries:diary_detail',
            kwargs={'diary_slug': self.slug})

@receiver(post_delete, sender=Diary)
def diary_pictures_delete(sender, instance, **kwargs):
    instance.image.delete(False)
    delete_ckeditor_rich_text_images(instance.content)


class DiaryLike(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='liked_diaries')
    diary = models.ForeignKey(
        Diary,
        on_delete=models.CASCADE,
        related_name='diary_likes')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'diary']

    def __str__(self):
        return '{} : {} ({})'.format(self.user, self.diary, self.created_on)


class Comment(models.Model):
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    diary = models.ForeignKey(
        Diary,
        related_name='comments',
        on_delete=models.CASCADE)
    likes = models.ManyToManyField(
        Profile,
        related_name='liked_comments',
        through='CommentLike',
        through_fields=('comment', 'user'))
    author = models.ForeignKey(
        Profile,
        related_name='written_comments',
        on_delete=models.CASCADE)

    def __str__(self):
        return '{}... ({})'.format(self.content, self.author)


class CommentLike(models.Model):
    user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='comment_likes')
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_likes')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} : {} ({})'.format(
            self.user,
            self.comment,
            self.created_on)


@receiver(post_save, sender=DiaryLike)
def diary_like_create_handler(sender, instance, created, **kwargs):
    if instance.user != instance.diary.author:
        notify.send(
            sender=instance.user,
            recipient=instance.diary.author.user,
            target=instance.diary,
            verb='Liked')


@receiver(post_save, sender=Comment)
def comment_create_handler(sender, instance, created, **kwargs):
    if instance.author != instance.diary.author:
        notify.send(
            sender=instance.author,
            recipient=instance.diary.author.user,
            target=instance.diary,
            verb='Commented on')


@receiver(post_delete, sender=Diary)
def delete_notifications_when_diary_is_deleted(sender, instance, **kwargs):
    qs = Notification.objects.filter(target_object_id=instance.id)
    qs.delete()
