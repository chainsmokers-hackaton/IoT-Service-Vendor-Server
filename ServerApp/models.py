from django.db import models

class UploadFileModel(models.Model) :
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='files', null=True)