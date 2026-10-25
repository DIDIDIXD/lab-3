from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .forms import BookForm, UploadForm
from .utils import allowed_extension, list_files, parse_file, safe_filename, save_file
from django.conf import settings


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            data = {
                'title': form.cleaned_data['title'],
                'author': form.cleaned_data['author'],
                'year': form.cleaned_data['year'],
                'isbn': form.cleaned_data['isbn'],
                'pages': form.cleaned_data['pages'] or 0,
            }
            path = save_file([data], form.cleaned_data['format'])
            messages.success(request, f'Сохранено в {path.name}')
            return redirect('books:files')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            ext = allowed_extension(f.name)
            if not ext:
                messages.error(request, 'Разрешены только .json и .xml')
                return redirect('books:upload')

            path = settings.UPLOAD_DIR / safe_filename(ext)
            with open(path, 'wb+') as dest:
                for chunk in f.chunks():
                    dest.write(chunk)

            try:
                parse_file(path, ext)
            except ValidationError as e:
                path.unlink(missing_ok=True)
                messages.error(request, f'Файл невалиден и удалён: {e.messages[0]}')
            else:
                messages.success(request, f'Файл {path.name} загружен.')
                return redirect('books:files')
    else:
        form = UploadForm()
    return render(request, 'books/upload.html', {'form': form})


def file_list(request):
    return render(request, 'books/file_list.html', {'files': list_files()})