from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='Тестовый слаг',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(
            expected_object_name,
            str(group),
            'Убедитесь что метод __str__ работает правильно'
        )

    def test_models_have_correct_object_names_text(self):
        """Проверяем, что у class Post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(
            post.text[:15],
            str(post),
            'Убедитесь что метод __str__ работает правильно'
        )
