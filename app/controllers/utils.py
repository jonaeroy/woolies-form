from ferris import Controller, route_with
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import app_identity

from dateutil import tz
from datetime import datetime


class Utils(Controller, blobstore_handlers.BlobstoreDownloadHandler):

    @classmethod
    def convertStatus(self, svar):

        if(svar == 1):
            convStat = "Pending Approval"
        elif(svar == 2):
            convStat = "Temporarily Approved"
        elif(svar == 3):
            convStat = "Approved"
        elif(svar == 4):
            convStat = "Rejected"
        else:
            convStat = "No Action Required"

        return convStat

    @classmethod
    def revertStatus(self, svar):

        if(svar == "Pending Approval"):
            convStat = 1
        elif(svar == "Temporarily Approved"):
            convStat = 2
        elif(svar == "Approved"):
            convStat = 3
        elif(svar == "Rejected"):
            convStat = 4
        else:
            convStat = "No Action Required"

        return convStat

    @classmethod
    def StatusTextToId(self, statusText):

        status_code = self.revertStatus(statusText)

        if (isinstance(status_code, int) is not True):
            raise Exception("Status text: [%s] failed to be converted to a valid value." % (statusText,))

    @route_with(template='/attachment/<blob_key>')
    def serve_file(self, blob_key):
        from google.appengine.ext import blobstore

        if not blobstore.get(blob_key):
            raise NameError('File Not Found')
        else:
            blob_info = blobstore.BlobInfo.get(blob_key)
            self.send_blob(blob_key, save_as=blob_info.filename)
            return self.response

    @classmethod
    def generate_download_link(self, blob_key):
        from google.appengine.ext import blobstore
        if blob_key is None:
            return
        else:
            blob_info = blobstore.BlobInfo.get(blob_key)
            domain_path = 'http://' + str(app_identity.get_default_version_hostname())
            html = '<a target="_blank" class=download_link href="' + domain_path + '/attachment/' + str(blob_key) + '" title="Click to Download Attachment">' + blob_info.filename + '</a>'
            return html

    @classmethod
    def localize_datetime(self, date_time):

        fmt = '%Y-%m-%d %H:%M:%S'
        fmt2 = '%b %d, %Y %I:%M %p'

        from_zone = tz.gettz('UTC')
        #to_zone = tz.gettz('Asia/Manila')
        to_zone = tz.gettz('Australia/Sydney')

        utc = datetime.strptime(str(date_time)[:19], fmt)
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)

        vardtime = central.strftime(fmt2)

        return vardtime

    @classmethod
    def html_escape(self, text):
        """Produce entities within text."""

        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;"
        }

        return "".join(html_escape_table.get(c, c) for c in text)

    @classmethod
    def localize_date(self, dateparam):
        fmt = '%Y-%m-%d'
        fmt2 = '%b %d, %Y'

        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Australia/Sydney')
        #to_zone = tz.gettz('Asia/Manila')

        utc = datetime.strptime(str(dateparam)[:11], fmt)
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)

        vardtime = central.strftime(fmt2)

        return vardtime
