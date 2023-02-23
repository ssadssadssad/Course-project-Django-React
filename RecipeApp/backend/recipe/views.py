from rest_framework import generics
from .models import Recipe, Bookmarks, Category, Comment
from .serializers import RecipeSerializer, RecipeDetailsSerializer, RecipeBookmarkDetailSerializer, RecipeBookmarkListSerializer, RecipeBookmarkCreateSerializer, CategorySerializer, CommentSerializer, RecipeCreateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import get_or_none
from django.core.exceptions import ValidationError

#контроллеры, обработка запросов
class RecipeList(generics.ListAPIView):
    queryset = Recipe.postobjects.all()
    serializer_class = RecipeSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['category', ]


class RecipeCreate(generics.CreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    parser_classes = [MultiPartParser, FormParser]


class RecipeDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.postobjects.all()
    serializer_class = RecipeDetailsSerializer


class RecipeBookmarkList(generics.ListCreateAPIView):
    queryset = Bookmarks.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeBookmarkCreateSerializer
        return RecipeBookmarkListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(bookmarked_by=self.request.user)

    def perform_create(self, serializer):
        recipe_id = self.request.data.get("recipe", None)
        recipe = Recipe.objects.get(id=recipe_id)
        bookmark = Bookmarks.objects.filter(recipe=recipe, bookmarked_by=self.request.user)
        if bookmark.exists():
            raise ValidationError('Already in bookmarked list')
        serializer.save(recipe=recipe)


class RecipeBookmarkDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeBookmarkDetailSerializer
    lookup_field = 'recipe'

    def get_object(self):
        recipe = self.kwargs["recipe"]
        user = self.request.user
        return get_or_none(Bookmarks, recipe=recipe, bookmarked_by=user)


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PostComment(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
