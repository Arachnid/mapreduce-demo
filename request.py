from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import os

import model


class BaseHandler(webapp.RequestHandler):
  def render_template(self, filename, template_args):
    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    self.response.out.write(template.render(path, template_args))


class IndexHandler(BaseHandler):
  def get(self):
    files = model.ZipFile.all().fetch(20)
    jobs = model.CodesearchJob.all().order('-created').fetch(20)
    self.render_template("index.html", {
        "files": files,
        "jobs": jobs,
    })


class JobHandler(BaseHandler):
  def get(self, job_id):
    job = model.CodesearchJob.get_by_id(int(job_id))
    results = model.CodesearchResults.all().ancestor(job).fetch(500)
    self.render_template("job.html", {
        "job": job,
        "results": results,
    })


class UploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
  def get(self):
    self.render_template("upload.html", {
        "form_url": blobstore.create_upload_url("/upload"),
        "id": self.request.GET.get("id", None),
    })

  def post(self):
    info = self.get_uploads("file")[0]
    file = model.ZipFile(filename=info.filename, blob=info)
    file.put()
    self.redirect("/")


application = webapp.WSGIApplication([
  ('/', IndexHandler),
  ('/upload', UploadHandler),
  ('/job/(\d+)', JobHandler),
], debug=True)


def main():
  run_wsgi_app(application)


if __name__ == "__main__":
  main()
