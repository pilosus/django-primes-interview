from django import forms


class UploadFileForm(forms.Form):
    """
    Render a form for json-file upload.
    """
    upload = forms.FileField(label="Datasets in JSON format")