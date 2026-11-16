from apps import celery

from apps.myob import myobreader


# @celery.task()
# def read_sageone_write_reckon_task(job_id):
#     try:
#         # myob_data_reader.start_read_operation(job_id)
#         myobreader.read_data(job_id)
#         return True
#     except Exception as ex:
#         print(ex)
#         return False

def read_sageone_write_reckon_task(job_id):
    try:
        print("=======data=======")
        # myob_data_reader.start_read_operation(job_id)
        myobreader.read_data(job_id)
        return True
    except Exception as ex:
        print(ex)
        return False
    
def retry_reckon_write_task(job_id):

    try:
        myobreader.retry_write_data(job_id)
        return True
    except Exception as ex:
        print(ex)
        return False


