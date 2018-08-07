import os, time
from app import celery, report_dir


@celery.task
def delete_files():
    current_time = time.time()
    for f in os.listdir(report_dir):
        creation_time = os.path.getctime(os.path.join(report_dir, f))
        if current_time - creation_time >= 86400:
            os.remove(os.path.join(report_dir, f))
