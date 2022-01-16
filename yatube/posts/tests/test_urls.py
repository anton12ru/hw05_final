from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент с автором поста
        self.author = User.objects.get(id=self.group.id)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.template_url_names = {
            '': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }

    def test_urls_uses_correct_template_guest(self):
        """Проверяем страницы на доступность
        неавторизованому пользваотелю
        """
        for url, template in self.template_url_names.items():
            with self.subTest(template=template):
                if url != '/create/' and url != '/posts/1/edit/':
                    response = self.guest_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_author_user(self):
        """Проверяем страницы на доступность для автора поста"""
        for url, template in self.template_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_client(self):
        """Проверяем страницы на доступность для автоизованого юзера"""
        for url, template in self.template_url_names.items():
            with self.subTest(template=template):
                if url != '/posts/1/edit/':
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)

    def test_urls_available_to_guest(self):
        """Не авторизованный пользователь не может создать новый пост,
        он перенаправляется на страницу авторизации.
        """
        response = self.client.get(reverse('posts:post_create'), follow=True)
        url_next = '?next='
        self.assertRedirects(
            response,
            reverse('users:login') + url_next +
            reverse('posts:post_create')
        )
