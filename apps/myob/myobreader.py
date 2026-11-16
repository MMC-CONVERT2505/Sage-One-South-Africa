from apps.home.models import Task
from apps.myob.sageone_to_reckon_task import SageoneToReckonone

from apps import db
from os import path
from apps.home.models import Jobs, Tool
from apps.myconstant import *
from sqlalchemy.orm import aliased
from apps.mmc_settings.all_settings import *
from apps.home.data_util import add_job_status
from apps.util.log_file import log_config
from apps.reckon_one.excel_to_reckon_task import ExcelToReckon
from apps.home.data_util import update_task_execution_status, write_task_execution_step


def read_data(job_id):
    logging = log_config(job_id)
    print("read data")
    try:
        logging.info(f"{job_id} inside read_data")
        # GET MYOB data
        # job_details = db.session.query(Jobs).get(job_id)
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)
        read_result = db.session.execute(
            "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id", {"job_id": job_id})
        # Output the query result as JSON
        for row in read_result:
            input_tool = row[0]
            output_tool = row[1]
        # Get list of tasks added in the job

        # TODO: Check if input tool is excel
        # If yes push data to mongodb in respective tables with job id and task id and some status flag
        # indicating whether the records is pushed or not

        read_tasks = Task.query.filter(
            Task.job_id == job_id).filter(Task.read != 1).all()
        add_job_status(job_id, status=2)

        for task in read_tasks:
            print(task,"task details")

            if input_tool == SAGEONE and output_tool == RECKON:
                SageoneToReckonone.read_data(job_id, task)

            if input_tool == EXCEL and output_tool == RECKON:
                ExcelToReckon.read_data(job_id, task)
           
            db.session.close()

        write_result = db.session.execute(
            "select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id", {"job_id": job_id})
        # Output the query result as JSON
        for row in write_result:
            input_tool = row[0]
            output_tool = row[1]
        # Get list of tasks added in the job

        write_tasks = Task.query.filter(
            Task.job_id == job_id).filter(Task.write != 1).all()
        add_job_status(job_id, status=2)

        for task in write_tasks:

            if input_tool == SAGEONE and output_tool == RECKON:
                SageoneToReckonone.write_data(job_id, task)

            if input_tool == EXCEL and output_tool == RECKON:
                ExcelToReckon.write_data(job_id, task)

            db.session.close()

    except Exception as ex:
        logging.error(ex, exc_info=True)


def retry_write_data(job_id):
    print("inside retry write data-------------")
    try:
        tool1 = aliased(Tool)
        tool2 = aliased(Tool)
      
       
        write_result = db.session.execute("select t1.account_type as input ,t2.account_type as output from jobs inner join tool t1 on t1.id=jobs.input_account_id inner join tool t2 on t2.id=jobs.output_account_id where jobs.id=:job_id", {"job_id":job_id})

        print(write_result,"write_results ========")
        for row in write_result:
            input_tool=row[0]
            output_tool=row[1]
        
        write_tasks = Task.query.filter(Task.job_id == job_id).filter().all()
        
        add_job_status(job_id, status=2)
        

        for task in write_tasks:

            if input_tool == SAGEONE and output_tool == RECKON:
                print("inside reckon tool data")
                update_task_execution_status(task.id, status=3, task_type="write")

                SageoneToReckonone.write_data(job_id, task)

            
            
            db.session.close()

        
       

    except Exception as ex:
        print(ex)

