import thriftpy
from django.conf import settings
from django.contrib.sites.models import Site
from thriftpy.rpc import make_client
from thriftpy.thrift import TException

timestamp_thrift = thriftpy.load('./thrift/timestamper.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService

def timestamp_view(request):
    try:
        client = make_client(Timestamp,
                             Site.objects.get_current().domain + '/timestamp/',
                             settings.TIMESTAMP_SERVICE_PORT
                             )

        timestamp_string = client.timestamp()

        return timestamp_string
    except TException as e:
        print(e)
    return None
