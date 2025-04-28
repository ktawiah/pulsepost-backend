from rest_framework import serializers

from apps.posts.models import Comment, Like, Post, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer definition for the Tag model."""

    url = serializers.HyperlinkedIdentityField(view_name="tag-detail", lookup_field="pk", read_only=True)
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            "id",
            "url",
            "name",
            "slug",
            "created_at",
            "updated_at",
            "posts_count",
        ]

    def get_posts_count(self, obj):
        return obj.posts.count()


class TagCreateSerializer(serializers.ModelSerializer):
    """Serializer definition for creating a Tag."""

    class Meta:
        model = Tag
        fields = [
            "name",
        ]


class PostSerializer(serializers.ModelSerializer):
    """Serializer definition for the Post model."""

    url = serializers.HyperlinkedIdentityField(view_name="post-detail", lookup_field="pk", read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "url",
            "user",
            "title",
            "content",
            "created_at",
            "updated_at",
            "status",
            "likes",
            "comments_count",
            "likes_count",
            "is_liked",
            "tags",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.post_likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.post_likes.filter(user=request.user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer definition for the Post model."""

    class Meta:
        model = Post
        fields = [
            "user",
            "title",
            "content",
            "status",
            "tags",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer definition for the Comment model."""

    url = serializers.HyperlinkedIdentityField(view_name="comment-detail", lookup_field="pk", read_only=True)
    replies_count = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "url",
            "user",
            "user_email",
            "post",
            "content",
            "created_at",
            "updated_at",
            "parent",
            "replies_count",
        ]

    def get_replies_count(self, obj):
        return obj.replies.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer definition for creating a Comment."""

    class Meta:
        model = Comment
        fields = [
            "user",
            "post",
            "content",
            "parent",
        ]


class LikeSerializer(serializers.ModelSerializer):
    """Serializer definition for the Like model."""

    url = serializers.HyperlinkedIdentityField(view_name="like-detail", lookup_field="pk", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Like
        fields = [
            "id",
            "url",
            "user",
            "user_email",
            "post",
            "post_title",
            "created_at",
        ]


class LikeCreateSerializer(serializers.ModelSerializer):
    """Serializer definition for creating a Like."""

    class Meta:
        model = Like
        fields = [
            "user",
            "post",
        ]
