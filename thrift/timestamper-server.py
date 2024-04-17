import threading
import thriftpy
from thriftpy.rpc import make_server
from datetime import datetime
from django.conf import settings

timestamp_thrift = thriftpy.load('/timestamper.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService


class TimestampHandler:
    def timestamp(self):
        return datetime.timestamp(datetime.now())


if __name__ == '__main__':
    server = make_server(Timestamp, TimestampHandler(), settings.TIMESTAMP_SERVICE_PORT)
    server.serve()
    # todo: use threading library to spawn a thread from the main django process to run this server on runserver_plus

