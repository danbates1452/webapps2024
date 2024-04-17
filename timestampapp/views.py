from datetime import datetime

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response


def get_current_posix_timestamp():
    return datetime.timestamp(datetime.now())


def timestamp_view(request):
    return Response(data=get_current_posix_timestamp())
