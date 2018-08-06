import os, time
from app import celery, app, UploadDir


@celery.task
def delete_files():
    upload_report = os.path.join(app.root_path, UploadDir['ReportFolder'])
    current_time = time.time()
    for f in os.listdir(upload_report):
        creation_time = os.path.getctime(os.path.join(upload_report, f))
        if current_time - creation_time >= 86400:
            os.remove(os.path.join(upload_report, f))
