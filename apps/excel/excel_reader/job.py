import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path


def get_excel_job(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_job"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        job_data = pd.read_excel(path, 'Job')

        for index, row in job_data.iterrows():
            
            job_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error":None,
                "payload":None,
                "Number": row["Job number"],
                "Name": str(row["Job name"]),
                "IsHeader": False,
                }
            
            collection.insert_one(job_payload)


    except Exception as ex:
        traceback.print_exc()
        