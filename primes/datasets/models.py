from django.db import models

# TODO: it might not yet have a value for its primary key field.
# https://docs.djangoproject.com/en/1.10/ref/models/fields/#filefield
def file_upload(instance, filename):
    """
    File will be uploaded to MEDIA_ROOT/<dataset_id>.json
    """
    return '{id}.json'.format(id=instance.pk)


class Dataset(models.Model):
    upload = models.FileField()
    input = models.TextField()
    result = models.TextField()
    status = models.NullBooleanField(default=None)
    exception_message = models.CharField(max_length=255)
    added = models.DateField(auto_now_add=True)
    checked = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{filename} {timestamp}".format(filename=self.upload.filename,
                                               timestamp=self.added)
