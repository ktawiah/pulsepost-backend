from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.posts.api.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    LikeCreateSerializer,
    LikeSerializer,
    PostSerializer,
    TagCreateSerializer,
    TagSerializer,
)
from apps.posts.models import Comment, Like, Post, Status, Tag


class IsOwnerOrReadOnly:
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET']:
            return True
        return obj.user == request.user


class PostViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()

    def list(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        search_query = request.query_params.get("search")
        tag_slug = request.query_params.get("tag")
        
        queryset = self.get_queryset()
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            ).order_by("-updated_at")
        elif tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug).order_by("-updated_at")
        else:
            queryset = queryset.order_by("-updated_at")

        instance = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(instance=instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request) -> Response:
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = PostSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = PostSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['user'] = request.user.id
        
        # Validate status transitions
        if 'status' in data and instance.status != data['status']:
            if instance.status == Status.ARCHIVED.value and data['status'] != Status.DRAFT.value:
                return Response(
                    {"status": "Cannot change status from archived to anything other than draft"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = PostSerializer(instance, data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        if 'user' in data:
            data['user'] = request.user.id
        
        # Validate status transitions
        if 'status' in data and instance.status != data['status']:
            if instance.status == Status.ARCHIVED.value and data['status'] != Status.DRAFT.value:
                return Response(
                    {"status": "Cannot change status from archived to anything other than draft"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = PostSerializer(instance, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=False)
    def recent_posts(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        queryset = self.get_queryset().filter(status=Status.PUBLISHED.value).order_by("-updated_at")
        instance = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False)
    def my_posts(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        queryset = self.get_queryset().filter(user=request.user).order_by("-updated_at")
        instance = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CommentViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.all()

    def list(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        post_id = request.query_params.get("post")
        if post_id:
            queryset = self.get_queryset().filter(post_id=post_id, parent=None)
        else:
            queryset = self.get_queryset().filter(parent=None)
            
        instance = paginator.paginate_queryset(queryset, request)
        serializer = CommentSerializer(instance=instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request) -> Response:
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CommentCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = CommentSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['user'] = request.user.id
        data['post'] = instance.post.id
        if 'parent' in data:
            data['parent'] = instance.parent.id if instance.parent else None
        
        serializer = CommentSerializer(instance, data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        if 'user' in data:
            data['user'] = request.user.id
        if 'post' in data:
            data['post'] = instance.post.id
        if 'parent' in data:
            data['parent'] = instance.parent.id if instance.parent else None
        
        serializer = CommentSerializer(instance, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=True)
    def replies(self, request, pk=None):
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        instance = get_object_or_404(self.get_queryset(), pk=pk)
        queryset = instance.replies.all()
        instance = paginator.paginate_queryset(queryset, request)
        serializer = CommentSerializer(instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class LikeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def get_queryset(self):
        return Like.objects.all()

    def list(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        post_id = request.query_params.get("post")
        if post_id:
            queryset = self.get_queryset().filter(post_id=post_id)
        else:
            queryset = self.get_queryset()
            
        instance = paginator.paginate_queryset(queryset, request)
        serializer = LikeSerializer(instance=instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request) -> Response:
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = LikeCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = LikeSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.all()

    def list(self, request: Request) -> Response:
        paginator = PageNumberPagination()
        if request.query_params.get("page_size"):
            paginator.page_size = request.query_params.get("page_size")
        else:
            paginator.page_size = 10

        search_query = request.query_params.get("search")
        if search_query:
            queryset = self.get_queryset().filter(name__icontains=search_query)
        else:
            queryset = self.get_queryset()
            
        instance = paginator.paginate_queryset(queryset, request)
        serializer = TagSerializer(instance=instance, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def create(self, request: Request) -> Response:
        serializer = TagCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = TagSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = TagSerializer(instance, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = TagSerializer(instance, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
