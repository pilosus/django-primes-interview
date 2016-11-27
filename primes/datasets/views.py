from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Index page
    :param request: Request
    :return: HttpResponse
    """
    context = {'page': 'home'}
    return render(request, 'datasets/index.html', context)


def submit(request):
    context = {'page': 'submit'}
    return render(request, 'datasets/submit.html', context)


def process(request):
    context = {'page': 'process'}
    return render(request, 'datasets/process.html', context)
