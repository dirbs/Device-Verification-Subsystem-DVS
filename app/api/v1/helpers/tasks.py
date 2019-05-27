import os
from time import sleep, time
from celery.signals import task_postrun

from app import celery, app, db
from .bulk_common import BulkCommonResources
from ..models.summary import Summary
from celery.result import AsyncResult


class CeleryTasks:

    @staticmethod
    @celery.task
    def get_summary(imeis_list, invalid_imeis):
        """Celery task for bulk request processing."""
        try:
            imeis_chunks = BulkCommonResources.chunked_data(imeis_list)
            records, invalid_imeis, unprocessed_imeis = BulkCommonResources.start_threads(imeis_list=imeis_chunks,
                                                                                          invalid_imeis=invalid_imeis)
            # send records for summary generation
            response = BulkCommonResources.build_summary(records, invalid_imeis, unprocessed_imeis)

            return {"response": response, "task_id": celery.current_task.request.id}
        except Exception as e:
            app.logger.exception(e)
            return {"response": {}, "task_id": celery.current_task.request.id}

    @staticmethod
    @celery.task()
    def log_results(response, input):
        try:
            status = AsyncResult(response['task_id'])
            while not status.ready():
                sleep(0.5)
            if response['response']:
                Summary.update(input=input, status=status.state, response=response)
            else:
                Summary.update(input=input, status='FAILURE', response=response)
            return True
        except Exception:
            Summary.update(input=input, status='FAILURE', response=response)
            return True


    @staticmethod
    @celery.task
    def delete_files():
        """Deletes reports from system after a specific time."""
        try:
            current_time = time()  # get current time
            for f in os.listdir(app.config['dev_config']['UPLOADS']['report_dir']):  # list files in specific directory
                creation_time = os.path.getctime(
                    os.path.join(app.config['dev_config']['UPLOADS']['report_dir'], f))  # get creation time of each file
                if current_time - creation_time >= app.config['system_config']['global']['CompliantReportDeletionTime']*3600:  # compare creation time is greater than 24 hrs
                    os.remove(os.path.join(app.config['dev_config']['UPLOADS']['report_dir'],
                                           f))  # if yes, delete file from directory
        except Exception as e:
            app.logger.exception(e)
            raise e

    @task_postrun.connect
    def close_session(*args, **kwargs):
        # Flask SQLAlchemy will automatically create new sessions for you from
        # a scoped session factory, given that we are maintaining the same app
        # context, this ensures tasks have a fresh session (e.g. session errors
        # won't propagate across tasks)
        db.session.remove()

