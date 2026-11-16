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
from datetime import datetime
import math
import collections
from apps.util.qbo_util import instance_check


def get_excel_payroll_payschedules(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payrollSchedules"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path, 'Pay Schedules')
        
        instance_name = None
        for index, row in leave_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            
            payfrequency_map = {
                "Weekly": 1,
                "Fortnightly": 2,
                "Monthly": 3
            }
            
            if row['Pay frequency'] in payfrequency_map:
                payfrequency = payfrequency_map[row["Pay frequency"]]
            QuerySet['PayFrequency'] = payfrequency
            QuerySet['Name'] = str(row['Pay schedule name'])

            start_date=str(row['First pay period start date']).split(" ")[0]
            start_date1 = datetime.strptime(start_date, "%Y-%m-%d")
            start_date2=start_date1.strftime("%Y-%m-%d")  


            end_date=str(row['First pay date']).split(" ")[0]
            end_date1 = datetime.strptime(end_date, "%Y-%m-%d")
            end_date2=end_date1.strftime("%Y-%m-%d")


            next_date=str(row['First pay date']).split(" ")[0]
            next_date1 = datetime.strptime(next_date, "%Y-%m-%d")
            next_date2=next_date1.strftime("%Y-%m-%d")


            QuerySet['StartPayPeriodDate'] = start_date2
            QuerySet['EndPayPeriodDate'] = end_date2
            QuerySet['NextPaymentDate'] = next_date2

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
