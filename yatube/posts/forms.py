from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
            'group',
            'image',
        ]
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа, к которой будет относиться пост'),
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группы'
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError(
                "Пожалуйста заполните поле 'Текст поста'"
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
