import os, time
from app import celery, UploadDir


@celery.task
def delete_files():
    current_time = time.time()
    for f in os.listdir(UploadDir['ReportFolder']):
        creation_time = os.path.getctime(os.path.join(UploadDir['ReportFolder'], f))
        if current_time - creation_time >= 86400:
            os.remove(os.path.join(UploadDir['ReportFolder'], f))
