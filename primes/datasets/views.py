from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Index page
    :param request: Request
    :return: HttpResponse
    """
    return render(request, 'datasets/index.html')


def submit(request):
    return render(request, 'datasets/submit.html')


def process(request):
    return render(request, 'datasets/process.html')
