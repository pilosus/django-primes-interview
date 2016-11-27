import re
from django.utils import timezone


def handle_uploaded_file(instance, filename):
    """
    Return a path to a file under MEDIA_ROOT directory.

    :param instance: An instance of the model where the FileField is defined
    :param filename: The filename that was originally given to the file.
    :return: A path to where file is to be saved at.
    """
    timestamp = re.sub(r'\.|:| |e|\+', '-', str(timezone.now()))
    return "uploads/{0}.json".format(timestamp)
