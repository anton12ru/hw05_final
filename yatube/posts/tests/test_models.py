from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.user_2 = User.objects.create(username='Saraj')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='Тестовый слаг',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='text comment',
            author=cls.user,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_2,
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

    def test_models_post_have_correct_object_names_text(self):
        """Проверяем, что у class Post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(
            post.text[:15],
            str(post),
            'Убедитесь что метод __str__ работает правильно'
        )

    def test_models_comment_have_correct_object_names_text(self):
        """Проверяем, что у class Comment корректно работает __str__."""
        text_comment = PostModelTest.comment
        self.assertEqual(
            text_comment.text,
            str(text_comment),
        )

    def test_metaclass_follow_is_unique(self):
        """Проверяем что подписки являются уникальными класса Follow"""
        follow = Follow.objects.get(id=self.follow.id)
        follow_unique = follow._meta.unique_together
        self.assertEqual(follow_unique[0], ('user', 'author'))

    def test_models_follow_method_str(self):
        """Убедимся, что метод __str__ класса Follow работает правильно."""
        user_follower = PostModelTest.follow
        self.assertEqual(
            user_follower.user.username,
            str(user_follower),
        )
