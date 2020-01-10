from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .serializers import DiaryListSerializer, DiaryDetailSerializer
from ..models import Diary


class StandardPagination(PageNumberPagination):
    page_size = 9


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
        order_by = self.request.GET.get('order_by', None)
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
