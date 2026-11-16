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


def get_excel_payroll_deduction(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payrolldeduction"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        deduction_data = pd.read_excel(path, 'Payroll_deduction')
        grouped_data = deduction_data

        template1 = list(
            dbname['reckon_vendorcredit_template'].find({"job_id": job_id}))

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

                subtype_map = {
                    "Other (Deductions)": 16,
                    "Union Fees (Deductions)": 17,
                    "Workplace Giving (Deductions)": 18
                }

                calculationbasictype_map = {
                    "Quantity": 1,
                    "Hourly": 2,
                    "Other": 3

                }

                if row['CalculationBasicType'] in calculationbasictype_map:
                    calculationtype = calculationbasictype_map[row["CalculationBasicType"]]
                else:
                    calculationtype = 0

                if row["SubTypeId"] in subtype_map:
                    SubTypeId = subtype_map[row["SubTypeId"]]
                else:
                    SubTypeId = 0

                if row["Deduction type"] in payitemtype_map:
                    payitemtype = payitemtype_map[row["Deduction type"]]
                else:
                    payitemtype = 0

                QuerySet['Name'] = str(row['Deduction item name'])
                QuerySet['PayItemType'] = payitemtype
                QuerySet['SubTypeId'] = SubTypeId
                QuerySet['CalculationBasisType'] = calculationtype
                QuerySet['DefaultRate'] = str(row["DefaultRate"])
                QuerySet['IsPercentValue'] = str(row["Ispercentvalue"])
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
