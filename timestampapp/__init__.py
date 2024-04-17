import threading
from datetime import datetime

import thriftpy
from django.conf import settings
from django.contrib.sites.models import Site
from thriftpy.rpc import make_server

timestamp_thrift = thriftpy.load('./thrift/timestamper.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService


class TimestampHandler:
    def timestamp(self):
        return datetime.timestamp(datetime.now())

print(Site.objects.get_current().domain + '/timestamp/')
server = make_server(Timestamp, TimestampHandler(), Site.objects.get_current().domain + '/timestamp/', settings.TIMESTAMP_SERVICE_PORT)

ts_thread = threading.Thread(server.serve())
ts_thread.start()
print('timestamp service started')
