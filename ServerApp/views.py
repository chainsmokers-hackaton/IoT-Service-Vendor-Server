import logging
import json

from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ServerApp.functions import *
from ServerApp.models import UploadFileModel

logger = logging.getLogger(__name__)

@csrf_exempt
def alert_view(request):
    global logger
    if request.method == 'POST':
        logger.info("Request from Client.")

        alert_data = json.loads(request.body)
        ResponseToSecurityIssue(alert_data)

        logger.info("Result response to Client")
        return HttpResponse('result')

@csrf_exempt
def upload_file_view(request):
    global  logger
    if request.method == 'POST':
        logger.info("Request from Client.")

        newFile = UploadFileModel(file=request.FILES["file"])
        newFile.save()
        es = ElasticsearchWrapper(newFile)
        es.insert_to_elasticsearch()

        logger.info("Result response to Client")
        return HttpResponse('result')