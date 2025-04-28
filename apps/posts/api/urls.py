from django.urls import path

from .views import CommentViewSet, LikeViewSet, PostViewSet, TagViewSet

post_list = PostViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

post_detail = PostViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

recent_posts = PostViewSet.as_view(
    {
        "get": "recent_posts",
    }
)

my_posts = PostViewSet.as_view(
    {
        "get": "my_posts",
    }
)

comment_list = CommentViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

comment_detail = CommentViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

comment_replies = CommentViewSet.as_view(
    {
        "get": "replies",
    }
)

like_list = LikeViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

like_detail = LikeViewSet.as_view(
    {
        "get": "retrieve",
        "delete": "destroy",
    }
)

tag_list = TagViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

tag_detail = TagViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("posts/", post_list, name="post-list"),
    path("posts/recent/", recent_posts, name="post-recent"),
    path("posts/my/", my_posts, name="post-my"),
    path("posts/<uuid:pk>/", post_detail, name="post-detail"),
    path("comments/", comment_list, name="comment-list"),
    path("comments/<uuid:pk>/", comment_detail, name="comment-detail"),
    path("comments/<uuid:pk>/replies/", comment_replies, name="comment-replies"),
    path("likes/", like_list, name="like-list"),
    path("likes/<uuid:pk>/", like_detail, name="like-detail"),
    path("tags/", tag_list, name="tag-list"),
    path("tags/<uuid:pk>/", tag_detail, name="tag-detail"),
]
