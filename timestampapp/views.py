from datetime import datetime, timezone

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


def get_current_posix_timestamp():
    return datetime.now(tz=timezone.utc).isoformat()


@api_view(('GET', ))
@renderer_classes((JSONRenderer,))
def timestamp_view(request):
    return Response(data=get_current_posix_timestamp())
