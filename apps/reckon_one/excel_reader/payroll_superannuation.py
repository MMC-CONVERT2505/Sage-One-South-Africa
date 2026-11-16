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


def get_excel_payroll_superannuation(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payrollsuperannuation"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        superannuation_data = pd.read_excel(path, 'Payroll_superannuation')
        grouped_data = superannuation_data

        Account_data = list(dbname["Reckon_account"].find({"job_id":job_id}))
         

        instance_name = None
        for group_index, df_group in grouped_data:
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            for row_index, row in df_group.iterrows():

                paysubtype_map = {
                    "Super Guarantee": 19,
                    "Employer Additional": 20,
                    "Productivity": 21,
                    "Collective Agreement": 22,
                    "Salary Sacrifice": 23,
                    "Member Voluntary": 24,
                    "Spouse Deduction": 25
                }
                account=None
                for j3 in range(0,len(Account_data)):
                    if str(row["Expense account"]) == Account_data[j3]['Name']:
                        account=Account_data[j3]["Id"]
                    

                if row["Superannuation type"] in paysubtype_map:
                    paysubtype = paysubtype_map[row["Superannuation type"]]
                else:
                    paysubtype = 0

                QuerySet['PaySubType'] = paysubtype
                QuerySet['Name'] = str(row['superannuation item name'])
                QuerySet['Description'] = str(row['Description'])
                QuerySet['IsSR'] = str(row['issr'])
                QuerySet["DefaultRate"]=str(row['Default rate'])
                
                QuerySet["ExpenseAccountId"]=account

                QuerySet['DeductGrossBeforeTax'] = str(
                    row['Deduct GrossBefore Tax'])

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
