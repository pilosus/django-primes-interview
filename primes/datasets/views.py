from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Dataset
from .forms import UploadFileForm


def index(request):
    """
    Index page
    :param request: Request
    :return: HttpResponse
    """
    context = {'page_alias': 'home'}
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

    context = {'page_alias': 'submit', 'form': form}
    return render(request, 'datasets/submit.html', context)


def process(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        # TODO: process data here
        messages.info(request, 'Datasets processing has started.')
        return redirect(reverse('datasets:process'))

    unprocessed_datasets = Dataset.objects.filter(checked__isnull=True)
    paginator = Paginator(unprocessed_datasets, 25)

    page = request.GET.get('page')
    print(page)
    try:
        datasets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        datasets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        datasets = paginator.page(paginator.num_pages)

    context = {'page_alias': 'process', 'datasets': datasets}
    return render(request, 'datasets/process.html', context)


def report(request):
    context = {'page_alias': 'report'}
    return render(request, 'datasets/report.html', context)