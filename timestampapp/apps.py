import threading
import time
from datetime import datetime
from django.apps import AppConfig
from django.conf import settings

import thriftpy
from thriftpy.rpc import make_server


class TimestampAppConfig(AppConfig):
    name = 'timestampapp'
    verbose_name = 'Timestamp Application'

    def ready(self):
        from django.contrib.sites.models import Site

        timestamp_thrift = thriftpy.load('./thrift/timestamper.thrift', module_name='timestamp_thrift')
        service = timestamp_thrift.TimestampService

        print('https://' + settings.ALLOWED_HOSTS[0] + '/timestamp/')
        server = make_server(service, TimestampHandler(), 'https://' + settings.ALLOWED_HOSTS[0] + '/timestamp/',
                             settings.TIMESTAMP_SERVICE_PORT)

        ts_thread = threading.Thread(delayed_method(server.serve()))
        ts_thread.start()
        print('timestamp service started')


class TimestampHandler:
    def timestamp(self):
        return datetime.timestamp(datetime.now())


def delayed_method(method):
    time.sleep(5)
    method()
