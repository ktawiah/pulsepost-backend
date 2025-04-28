from enum import Enum
from uuid import uuid4

from django.db import models
from django.utils.translation import gettext as _

from apps.accounts.models import User


class Status(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Tag(models.Model):
    """Model definition for Tag."""

    id = models.UUIDField(
        _("id"),
        default=uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        db_index=True,
    )
    name = models.CharField(_("name"), max_length=50, unique=True, db_index=True)
    slug = models.SlugField(_("slug"), unique=True, db_index=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        """Meta definition for Tag."""

        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        """Unicode representation of Tag."""
        return self.name


class Post(models.Model):
    """Model definition for Post."""

    id = models.UUIDField(
        _("id"),
        default=uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        db_index=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=255, db_index=True)
    content = models.TextField(_("content"))
    featured_image = models.ImageField(_("featured image"), upload_to="images", blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now_add=True)
    status = models.CharField(
        _("status"),
        max_length=11,
        choices=Status.choices(),
        default=Status.DRAFT,
    )
    likes = models.IntegerField(_("likes"), default=0)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    class Meta:
        """Meta definition for Post."""

        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        """Unicode representation of Post."""
        return self.title


class Comment(models.Model):
    """Model definition for Comment."""

    id = models.UUIDField(
        _("id"),
        default=uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        db_index=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    class Meta:
        """Meta definition for Comment."""

        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]

    def __str__(self):
        """Unicode representation of Comment."""
        return f"{self.user.email} - {self.content[:50]}"


class Like(models.Model):
    """Model definition for Like."""

    id = models.UUIDField(
        _("id"),
        default=uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        db_index=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        """Meta definition for Like."""

        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ["user", "post"]

    def __str__(self):
        """Unicode representation of Like."""
        return f"{self.user.email} likes {self.post.title}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only increment likes count on creation
            self.post.likes += 1
            self.post.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.post.likes -= 1
        self.post.save()
        super().delete(*args, **kwargs)
