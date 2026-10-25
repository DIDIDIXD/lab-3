from django import forms


class BookForm(forms.Form):
    title = forms.CharField(max_length=200, label='Название')
    author = forms.CharField(max_length=200, label='Автор')
    year = forms.IntegerField(label='Год', min_value=1000, max_value=2100)
    isbn = forms.CharField(max_length=20, required=False, label='ISBN')
    pages = forms.IntegerField(min_value=0, required=False, initial=0, label='Страниц')
    format = forms.ChoiceField(
        choices=[('json', 'JSON'), ('xml', 'XML')],
        label='Формат',
        initial='json',
    )


class UploadForm(forms.Form):
    file = forms.FileField(label='Файл JSON или XML')