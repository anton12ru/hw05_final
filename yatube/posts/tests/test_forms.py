import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-link',
            description='Описание',
        )
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
        cls.posts = Post.objects.create(
            author=cls.user,
            text='text',
            group=cls.group,
            image=uploaded,
        )
        cls.comments = Comment.objects.create(
            author=cls.user,
            text='text comment',
            post=cls.posts,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Очищаем папку с файлами после тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        # Не авторизованный клиент
        self.guest_client = Client()
        # Создаем User
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создается Автор Постов
        self.author = User.objects.get(id=self.group.id)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post в базу данных,
        в том числе и картинки.
        """
        post_count = Post.objects.count()
        form_data = {
            'author': self.user.username,
            'text': self.posts.text,
            'image': self.posts.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user],)
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.user,
                text=self.posts.text,
                image=self.posts.image.name,
            ).exists()
        )
        self.assertEqual(form_data['author'], self.user.username)
        self.assertEqual(form_data['image'], self.posts.image)
        self.assertEqual(form_data['text'], self.posts.text)

    def test_update_post(self):
        """Проверяет что при редактирование поста, сохраняется новые данные"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'new_text',
            'author': self.user.username,
            'group': self.group.id,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.group.id}),
            data=form_data,
            follow=True,
        )
        print(response.context)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.group.id})
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.user,
                text='new_text',
            ).exists()
        )

    def test_when_adding_comment_displayed_on_post_page(self):
        """Убедимся что при добавления комментария, он создается
        в БД и отображается на странице поста.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.comments.text,
            'author': self.comments.author,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.group.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.group.id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=self.comments.text,
                author=self.comments.author,
            ).exists()
        )
        self.assertEqual(
            Comment.objects.all()[0],
            response.context['comments'][0]
        )
        self.assertEqual(
            Comment.objects.all()[1],
            response.context['comments'][1]
        )

    def test_only_authorized_users_can_comment_on_post(self):
        """Убедимся что комментарий сможет добавить только авторизованный
        пользователь, неавторазиванный пользователь,
        будет перенаправлен на страницу авторизации.
        """
        comment_count = Comment.objects.count()
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.group.id}),
            follow=True,
        )
        url_next = '?next='
        self.assertRedirects(
            response,
            reverse('users:login') + url_next + reverse(
                'posts:add_comment', kwargs={'post_id': self.group.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comment_count)
