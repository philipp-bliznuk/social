from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import User, Post, Like
from .serializers import UserSerializer, PostSerializer


class UserRegistrationView(ListCreateAPIView, ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()

    @action(detail=True, methods=['post'], name='Like')
    def like(self, request, pk=None):
        user = self.get_object()
        post_id = request.data.get('post_id')
        post = Post.objects.filter(pk=post_id).exclude(likes__user=user).first()
        if user and post:
            Like.objects.create(user=user, post=post)
        return Response()

    @action(detail=True, methods=['post'], name='Dislike')
    def dislike(self, request, pk=None):
        user = self.get_object()
        post_id = request.data.get('post_id')
        Like.objects.filter(user=user, post_id=post_id).delete()
        return Response()

    @action(detail=False, methods=['get'], name='most-active-users')
    def get_most_active_users(self, request):
        users = User.objects.annotate(
            posts_count=Count('posts')
        ).annotate(
            likes_count=Count('posts__likes')
        ).order_by('-posts_count')
        return Response(
            {user.id: {'email': user.email, 'likes': user.likes_count} for user in users}
        )


class PostCreateView(ListCreateAPIView, ViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=False, methods=['post'], name='posts-by-other-authors')
    def get_posts_by_other_authors(self, request):
        author_id = request.data.get('author_id')
        users_with_0_likes_posts = Post.objects.filter(
            likes__isnull=True
        ).exclude(author_id=author_id).values_list('author_id', flat=True).distinct()

        return Response(
            Post.objects.filter(
                author_id__in=users_with_0_likes_posts
            ).values('id', 'title')
        )
