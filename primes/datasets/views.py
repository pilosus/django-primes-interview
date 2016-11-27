from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

from .models import Dataset
from .forms import UploadFileForm


def index(request):
    """
    Index page
    :param request: Request
    :return: HttpResponse
    """
    context = {'page': 'home'}
    return render(request, 'datasets/index.html', context)


def submit(request):
    """
    Submit a JSON dump file.

    We might want to set an upload size limit in settings.py like this:
    https://www.djangosnippets.org/snippets/1303/
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # save file on a model
            dataset = Dataset(upload=request.FILES['upload'])
            dataset.save()

            # set flash message
            messages.info(request, 'Your file has been submitted.')

            # POST -> Redirect -> GET
            return redirect(reverse('datasets:process'))
    # if GET, render an unbound form
    else:
        form = UploadFileForm()

    context = {'page': 'submit', 'form': form}
    return render(request, 'datasets/submit.html', context)


def process(request):
    context = {'page': 'process'}
    return render(request, 'datasets/process.html', context)
