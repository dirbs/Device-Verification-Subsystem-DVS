import os, time
from app import celery, report_dir


@celery.task
def delete_files():
    current_time = time.time()  # get current time
    for f in os.listdir(report_dir):  # list files in specific directory
        creation_time = os.path.getctime(os.path.join(report_dir, f))  # get creation time of each file
        if current_time - creation_time >= 86400:  # compare creation time is greater than 24 hrs
            os.remove(os.path.join(report_dir, f))  # if yes, delete file from directory
