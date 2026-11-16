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
from apps.util.log_file import log_config


def get_excel_payroll_earning_new(job_id, task_id):
    logging = log_config(job_id)
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
        earning_data = pd.read_excel(path, 'Pay Item Earning')
        grouped_data = earning_data

        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/superitems"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_superitems_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()
         

        instance_name = None
        for index, row in earning_data.iterrows():
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

            account = None
            if row["Expense account"] != "nan":
                for j3 in range(0, len(account_data)):
                    if str(row["Expense account"]) == account_data[j3]['Name']:
                        account = account_data[j3]["Id"]
                        break
            
            payrate_basis=None
            if row['Pay rate basis Houly'] =="True":
                payrate_basis=1
            else:
                payrate_basis=2

                
            earning_type=None
            if row["Earnings type"] =="Ordinary time earnings (OTE)":
                earning_type=8
            if row["Earnings type"] =="Overtime":
                earning_type=9
            if row["Earnings type"] =="Variable":
                earning_type=10
            if row["Earnings type"] =="Termination":
                earning_type=11
            if row["Earnings type"] =="Bonuses and Commisions": 
                earning_type=32
            if row["Earnings type"] =="Directors fees":
                earning_type=33
                

            description="-"
            if str(row["Description (optional)"]) =="nan" or str(row["Description (optional)"]) ==" ":
                description=" "
            else:
                description=str(row["Description (optional)"])

            QuerySet["Name"]=str(row["Earning item name"])
            QuerySet['Description'] = description
            QuerySet['RateMultiplier'] = str(row["Rate multiplier (optional)"])
            QuerySet["PayItemTypeName"] = "Earnings"
            QuerySet['PayItemType'] = 1
            QuerySet['SubTypeId'] = earning_type
            QuerySet['PayRateBasis'] = payrate_basis
            QuerySet["ExpenseAccountId"]=account
            QuerySet["IncludeInTimeAccruals"]=row["Include in time worked leave accurals"]
            QuerySet["TaxApplicableName"] = str(row["Calculation method"])  
            
            QuerySet["IncludedSuperItems"] = []

            super_garenty = {}
            if str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Super Guarantee"]) == "True" or str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Super Guarantee"]) == "1.0":
                for j3 in range(0, len(JsonResponse1)):
                    if "Super guarantee" == JsonResponse1[j3]['Name']:
                        super_garenty["id"] = JsonResponse1[j3]["PayItemId"] or JsonResponse1[j3]["Id"]
                        break
                QuerySet["IncludedSuperItems"].append(super_garenty)

            
            sacrifice_for_super = {}
            if str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Salary Sacrifice for super"]) == "True" or str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Salary Sacrifice for super"]) == "1.0":
                for j3 in range(0, len(JsonResponse1)):
                    if "Salary sacrifice for super" == JsonResponse1[j3]['Name']:
                        sacrifice_for_super["id"] = JsonResponse1[j3]["PayItemId"] or JsonResponse1[j3]["Id"]
                        break
        
                QuerySet["IncludedSuperItems"].append(sacrifice_for_super)
                

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
