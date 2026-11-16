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


def get_excel_reimbursement(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_reimbursement"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        reimbursement_data = pd.read_excel(path, 'Payroll_reimbursement')
        grouped_data = reimbursement_data

        instance_name = None
        for group_index, df_group in grouped_data:
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            for row_index, row in df_group.iterrows():

                payitemtype_map = {
                    "Earnings": 1,
                    "Allowance": 3,
                    "Deduction": 4,
                    "Reimbursement": 5
                }

                if row["reimbursement type"] in payitemtype_map:
                    payitemtype = payitemtype_map[row["reimbursement type"]]
                else:
                    payitemtype = 0

                QuerySet['Name'] = str(row['Reimbursement item name'])
                QuerySet['PayItemType'] = payitemtype

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
