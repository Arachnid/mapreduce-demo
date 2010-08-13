from google.appengine.ext import db
from google.appengine.ext import blobstore


class ZipFile(db.Model):
  filename = db.StringProperty(required=True)
  blob = blobstore.BlobReferenceProperty(required=True)


class CodesearchJob(db.Model):
  name = db.StringProperty()
  file = db.ReferenceProperty(ZipFile, required=True)
  regex = db.StringProperty(indexed=False)
  created = db.DateTimeProperty(required=True, auto_now_add=True)


class CodesearchResults(db.Model):
  filename = db.StringProperty(required=True)
  match_lines = db.ListProperty(int, required=True, indexed=False)
  matches = db.StringListProperty(required=True, indexed=False)

  @property
  def matches_with_lines(self):
    return zip(self.match_lines, self.matches)
