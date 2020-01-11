from rest_framework import serializers

from ..models import Diary, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    author_image = serializers.ReadOnlyField(source='author.image.url')

    class Meta:
        model = Comment
        fields = ['content', 'created_on', 'author_name', 'author_image']
        read_only_fields = ['created_on']


class DiaryListSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    author_image = serializers.ReadOnlyField(source='author.image.url')

    class Meta:
        model = Diary
        fields = ['title', 'slug', 'image', 'description', 'created_on',
                  'likes_count', 'comments_count', 'author_name',
                  'author_image']
        read_only_fields = ['slug', 'description',
                            'created_on', 'likes_count', 'comments_count']


class DiaryDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    author_image = serializers.ReadOnlyField(source='author.image.url')
    comments = CommentSerializer(many=True, read_only=True)
    # lookup_field = 'slug'

    class Meta:
        model = Diary
        fields = ['title', 'slug', 'image', 'content', 'created_on',
                  'likes_count', 'comments_count', 'author_name',
                  'author_image', 'feeling', 'is_visible', 'is_commentable',
                  'comments']
        read_only_fields = ['slug', 'created_on', 'likes_count',
                            'comments_count']
