import shutil
import tempfile

from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='auth')
        cls.user_1 = User.objects.create(username='jarah')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-link',
            description='Описание',
        )
        cls.posts = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
            image=uploaded,
        )
        cls.comments = Comment.objects.create(
            author=cls.user,
            text='comment',
            post=cls.posts
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_1,
        )
        cls.index_url = ('posts:index', 'posts/index.html', None)
        cls.group_url = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.group.slug,)
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            (cls.user.username,)
        )
        cls.paginator_url = (cls.index_url, cls.group_url, cls.profile_url)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Очищаем папку с файлами после тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        # Не авторизованный клиент
        self.guest_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = User.objects.get(id=self.group.id)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.group.id},
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.group.id},
            ): 'posts/create_post.html',
        }

    def test_pages_uses_correct_template(self):
        """Проверяем, что при обращении к name
        вызывается соответствующие HTML-шаблоны.
        """
        for reverses_name, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(reverses_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_page_with_show_correct_context_posts(self):
        """Проверка Paginator и шаблоны сформирован с правильным контекстом."""
        post_page_1 = 10
        post_page_2 = 4
        posts = [
            Post(
                text=f'posts #{num}',
                author=PostPagesTest.user,
                group=PostPagesTest.group,
            ) for num in range(1, (post_page_1 + post_page_2))
        ]
        Post.objects.bulk_create(posts)
        pages = [
            (1, post_page_1),
            (2, post_page_2),
        ]
        for name, _, args in PostPagesTest.paginator_url:
            for page, count in pages:
                with self.subTest(name=name, page=page):
                    response = self.authorized_client_author.get(
                        reverse(name, args=args), {'page': page}
                    )
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        count,
                    )

    def test_post_not_in_any_group(self):
        """Проверка, что созданный пост не попал в группу,
        для которой не был предназначен.
        """
        response = self.authorized_client_author.get(
            reverse('posts:group_list', args=[PostPagesTest.group.slug])
        )
        self.assertIn(
            self.posts, response.context.get('page_obj').object_list
        )

    def test_display_image_on_post_pages(self):
        # Не уверен что правильно написал тест.
        """Отображение картинки на странице с постами."""
        templates = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user},
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.posts.id},
            ),
        )
        for tamplate in templates:
            with self.subTest(tamplate=tamplate):
                response = self.guest_client.get(tamplate)
                post = response.content.decode('utf-8')
                img = '<img'
                self.assertIn(img, post)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cache_work(self):
        """Проверяем что кеш хранит данные даже после удаления поста,
        пост не показвается после принудельной очистки кеша.
        """
        post_1 = Post.objects.create(
            text='simple text, text',
            author=PostPagesTest.posts.author,
            image=PostPagesTest.posts.image,
            group=self.group,
        )
        response = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response, post_1)
        post_1.delete()
        response_2 = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response_2, post_1)
        cache.clear()
        response_3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response_3, post_1)

    def test_user_can_follow_other_users(self):
        """Авторизованный юзер, может подписаться на пользователя"""
        follow_count = Follow.objects.filter(
            user=self.user,
            author=self.follow.author,
        ).count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.user.username]),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_user_can_unsubscriptions(self):
        """Авторизованный юзер, может удалить из подписок пользователя"""
        follow_count = Follow.objects.filter(
            user=self.user,
            author=self.follow.author,
        ).count()
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                args=[self.follow.author.username]
            ), follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.follow.author.username])
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_new_post_user_appears_in_follow_index(self):
        """Новый пост пользователя отображается в ленте,
        в том случае, если пользователь подписан на автора.
        """
        post = Post.objects.create(
            author=self.follow.author,
            text='simple text.',
        )
        Follow.objects.create(
            user=self.user,
            author=self.follow.author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(post.text, response.content.decode('utf-8'))

    def test_new_post_user_not_appear_in_follow_index_not_following(self):
        """Убедимся, новый пост пользователя,
        не отображается, кто на него не подписан.
        """
        post = Post.objects.create(
            author=self.follow.author,
            text='simple text.',
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(post.text, response.content.decode('utf-8'))
