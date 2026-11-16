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


def get_excel_payroll_reimbursement(job_id, task_id):
    print("inside get_excel_reimbursement")
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_reimbursement"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        reimbursement_data = pd.read_excel(path, 'Pay Item Reimbursement')
        grouped_data = reimbursement_data
        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))

        instance_name = None
        for group_index, row in grouped_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None


            payitemtype_map = {
                    "Earnings": 1,
                    "Allowance": 3,
                    "Deduction": 4,
                    "Reimbursement": 5
                    }

         
            liability_account=None
            expense_account =None
            if str(row["Account"]) != "nan" or str(row["Account"]) != " ":
                for j3 in range(0,len(account_data)):
                    if str(row["Account"]) == account_data[j3]['Name']:
                        if account_data[j3]['AccountType']==4:
                            liability_account=account_data[j3]["Id"]
                            break
                        else:
                            expense_account=account_data[j3]["Id"]
                            break
                        

            QuerySet['Name'] = str(row['Reimbursement item name'])
            QuerySet['PayItemType'] = 5
            QuerySet['Description']=str(row['Description (optional)'])
            QuerySet["ExpenseAccountId"]=expense_account
            QuerySet["LiabilityAccountId"]=liability_account


            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
