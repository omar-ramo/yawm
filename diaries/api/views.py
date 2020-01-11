from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions

from .serializers import DiaryListSerializer, DiaryDetailSerializer
from ..models import Diary


class StandardPagination(PageNumberPagination):
    page_size = 9


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if obj.author == request.user.profile:
                return True
        return False


class DiaryListCreateAPIView(generics.ListCreateAPIView):
    model = Diary
    page_size = 9
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DiaryDetailSerializer
        return DiaryListSerializer

    def get_queryset(self):
        order_by = self.request.query_params.get('order_by', None)
        if order_by == 'popularity':
            qs = self.model.objects.popular()
        elif order_by == 'discover':
            qs = self.model.objects.all()
            qs = qs.active(self.request.user)
        else:
            if self.request.user.is_authenticated:
                followed_profiles_diaries = Diary.objects\
                    .by_followed_profiles(self.request.user.profile).order_by()

                current_profile_diaries = Diary.objects.filter(
                    author=self.request.user.profile
                ).order_by()

                qs = followed_profiles_diaries.union(current_profile_diaries)
                qs = qs.order_by('-created_on')
            else:
                qs = self.model.objects.all()
        return qs


class DiaryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'diary_slug'
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = DiaryDetailSerializer

    def get_queryset(self):
        qs = Diary.objects.active(self.request.user)
        return qs
