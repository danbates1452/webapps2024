import thriftpy
from thriftpy.rpc import make_client
from thriftpy.thrift import TException
from django.contrib.sites.models import Site
from django.conf import settings

timestamp_thrift = thriftpy.load('/timestamper.thrift', module_name='timestamp_thrift')

Timestamp = timestamp_thrift.TimestampService


def get_timestamp():
    try:
        client = make_client(Timestamp, Site.objects.get_current().domain, settings.TIMESTAMP_SERVICE_PORT)

        timestamp_string = client.timestamp()

        print(timestamp_string)
    except TException as e:
        print(e)


if __name__ == '__main__':
    get_timestamp()  # for debugging
