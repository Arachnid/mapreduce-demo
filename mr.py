from google.appengine.ext import db
from mapreduce import operation as op
from mapreduce import context

import re

import model


def codesearch_validator(user_params):
  """Validates and extends parameters for a codesearch MR."""
  file = model.ZipFile.get_by_id(int(user_params["file_id"]))
  user_params["blob_key"] = str(file.blob.key())

  parent_model = model.CodesearchJob(
    name=user_params["job_name"],
    file=file,
    regex=user_params["regex"])
  parent_model.put()
  user_params["parent_key"] = str(parent_model.key())

  return True


def codesearch((file_info, reader)):
  """Searches files in a zip for matches against a regular expression."""
  params = context.get().mapreduce_spec.mapper.params
  regex = re.compile(params["regex"])
  parent_key = db.Key(params["parent_key"])
  
  if file_info.file_size == 0:
    return

  results = model.CodesearchResults(
      parent=parent_key, filename=file_info.filename)
  file_data = reader()
  for line_no, line in enumerate(file_data.split('\n')):
    if regex.search(line):
      results.match_lines.append(line_no)
      results.matches.append(line.decode("utf-8", "ignore"))
  
  if results.matches:
    yield op.db.Put(results)
