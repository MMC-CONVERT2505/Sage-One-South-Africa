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


def get_excel_payroll_deduction(job_id, task_id):
    logging = log_config(job_id) 
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
        deduction_data = pd.read_excel(path, 'Payroll Deduction')
        grouped_data = deduction_data

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/contacts"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_contacts details_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/superitems"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_superitems_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse2 = response.json()
       
        
        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))

        instance_name = None
        for index, row in deduction_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            

            subtype_map = {
                    "Other (Deductions)": 16,
                    "Union Fees (Deductions)": 17,
                    "Workplace Giving (Deductions)": 18
                }

                
            SubTypeId=0
            if row["Deduction type"] in subtype_map:
                SubTypeId = subtype_map[row["Deduction type"]]
            else:
                SubTypeId = 0

           

            calculationtype=0
            if str(row['Calculation basis Hourly']) =="True" or str(row['Calculation basis Hourly']) =="TRUE" or str(row['Calculation basis Hourly']) =="1.0":
                calculationtype=1
            if str(row['Calculation basis Fixed amount']) =="True" or str(row['Calculation basis Fixed amount']) =="TRUE" or str(row['Calculation basis Fixed amount']) =="1.0":
                calculationtype=2
            if str(row['Calculation basis unit']) =="True" or str(row['Calculation basis unit']) =="TRUE" or str(row['Calculation basis unit']) =="1.0":
                calculationtype=3

            contact_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["IsSupplier"]:
                    if JsonResponse1[i]["Description"]==str(row['Supplier (optional)']):
                        contact_Id=JsonResponse1[i]["ContactId"]

            liability_account=None
            if str(row["Liability account"]) != "nan":
                for j3 in range(0,len(account_data)):
                    if str(row["Liability account"]) == account_data[j3]['Name']:
                        if account_data[j3]['AccountType']==4:
                            liability_account=account_data[j3]["Id"]
                            break
            
            limit_amount="0.01"
            if str(row["DEFAULT RATES (OPTIONAL) Limit"])=="nan" or str(row["DEFAULT RATES (OPTIONAL) Limit"])==" " or str(row["DEFAULT RATES (OPTIONAL) Limit"])=="0":
                limit_amount="0.01"
            else:
                limit_amount=str(row['DEFAULT RATES (OPTIONAL) Limit'])

            default_rate=0
            if str(row["DEFAULT RATES (OPTIONAL) Default rate"])=="nan" or str(row["DEFAULT RATES (OPTIONAL) Default rate"])==" ":
                default_rate=0
            else:
                default_rate=str(row["DEFAULT RATES (OPTIONAL) Default rate"])

                        
            QuerySet["LiabilityAccountId"]=liability_account
            QuerySet['Name'] = str(row['Deduction item name'])
            QuerySet['Description'] = str(row['Description (optional)'])
            QuerySet['PayItemType'] = 4
            QuerySet['SubTypeId'] = SubTypeId
            QuerySet['CalculationBasisType'] = calculationtype
            QuerySet['DefaultRate'] = default_rate
            QuerySet['LimitAmount'] = limit_amount
            QuerySet['IsPercentValue'] = "false"
            QuerySet["IsDeductedForTax"]=str(row["Deduct from gross before calculating withholding"])
            QuerySet["PayeeId"]=contact_Id

            QuerySet["IncludedSuperItems"] = []
            
            super_garenty = {}
            if str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Super Guarantee"]) == "True" or str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Super Guarantee"]) == "1.0":
                for j3 in range(0, len(JsonResponse2)):
                    if "Super guarantee" == JsonResponse2[j3]['Name']:
                        super_garenty["id"] = JsonResponse2[j3]["PayItemId"] or JsonResponse2[j3]["Id"]
                        break
                QuerySet["IncludedSuperItems"].append(super_garenty)

            
            sacrifice_for_super = {}
            if str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Salary Sacrifice for super"]) == "True" or str(row["SUPERANNUATION PREFERENCES (OPTIONAL) Include Salary Sacrifice for super"]) == "1.0":
                for j3 in range(0, len(JsonResponse2)):
                    if "Salary sacrifice for super" == JsonResponse2[j3]['Name']:
                        sacrifice_for_super["id"] = JsonResponse2[j3]["PayItemId"] or JsonResponse2[j3]["Id"]
                        break
        
                QuerySet["IncludedSuperItems"].append(sacrifice_for_super)


            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
