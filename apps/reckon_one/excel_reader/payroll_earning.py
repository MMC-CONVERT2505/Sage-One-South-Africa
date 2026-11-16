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


def get_excel_payroll_earning(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payrollearning"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        earning_data = pd.read_excel(path, 'Payroll_earning')
        grouped_data = earning_data

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

                payitemtype_map = {
                    "Earnings": 1,
                    "Allowance": 3,
                    "Deduction": 4,
                    "Reimbursement": 5
                }

                account=None
                for j3 in range(0,len(Account_data)):
                    if str(row["Expense account"]) == Account_data[j3]['Name']:
                        account=Account_data[j3]["Id"]
                    


                subtype_map = {
                    "Overtime (Earnings)": 9,
                    "Variable (Earnings)": 10,
                    "Termination (Earnings)": 11
                }

                PayRateBasis_map = {
                    "Hourly": 1,
                    "Salary": 2,
                }

                terminationtype_map = {
                    "Payment on death of an employee": "12752E20-4D3D-4A92-906E-1DC6CF48C1A6",
                    "All other termination payments": "4C6D52ED-A06D-42CA-8CD6-397AB5EAB43D",
                    "Invalidity": "B4C3CB5E-3F80-4A60-8E5B-4F4715FC75FB",
                    "Genuine redundancy": "087B68E5-B059-4459-A2A6-A12BA0EB442D",
                    "Compensation for unfair dismissal": "1E04CC05-FC17-43E9-8173-BB4F38D30321",
                    "Annual leave not accumulated in the system": "757A523D-0DB4-425D-BD78-BFD7D5652F73",
                    "Long service leave not accumulated in the system": "862C7DE5-C182-47FD-A729-EA0E04CBD59E"
                }
                Termination_field = "Termination"
                if row["Name"].lower() == Termination_field.lower():
                    if row["terminationtype"] in terminationtype_map:
                        termination_data = terminationtype_map[row["terminationtype"]]
                    else:
                        termination_data = 0
                    QuerySet['TerminationTypeId'] = termination_data

                if row['Pay rate basis'] in PayRateBasis_map:
                    PayRateBasis_data = PayRateBasis_map[row["Pay rate basis"]]
                else:
                    PayRateBasis_data = 0

                if row["SubTypeId"] in subtype_map:
                    SubTypeId = subtype_map[row["SubTypeId"]]
                else:
                    SubTypeId = 0

                if row["Earnings type"] in payitemtype_map:
                    payitemtype = payitemtype_map[row["Earnings type"]]
                else:
                    payitemtype = 0

                QuerySet['Name'] = str(row['Name'])
                QuerySet['PayItemType'] = payitemtype
                QuerySet['SubTypeId'] = SubTypeId
                QuerySet['PayRateBasis'] = PayRateBasis_data
                QuerySet['TaxApplicableName'] = str(row["Tax Application"])
                QuerySet['Description'] = str(row["Description (optional)"])
                QuerySet['Multiplier'] = str(row["Rate multiplier (optional)"])
                QuerySet["ExpenseAccountId"]=account
                QuerySet["IncludeInTimeAccruals"]=str(row["Include in time worked leave accurals"])

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
