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


def get_excel_payroll_company_contribution(job_id, task_id):
    logging = log_config(job_id) 
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payroll_company_contribution"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        company_contribution_data = pd.read_excel(path, 'Pay Item Company contribution')
        grouped_data = company_contribution_data

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/contacts"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_contacts details_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()
       
        
        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))
        
        instance_name = None
        for index, row in company_contribution_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            

        
            calculationtype=0
            if str(row['Calculation basis unit']) =="True" or str(row['Calculation basis Hourly']) =="TRUE" or str(row['Calculation basis Hourly']) =="1.0":
                calculationtype=1
            if str(row['Calculation basis Hourly']) =="True" or str(row['Calculation basis Fixed amount']) =="TRUE" or str(row['Calculation basis Fixed amount']) =="1.0":
                calculationtype=2
            if str(row['Calculation basis Fixed amount']) =="True" or str(row['Calculation basis unit']) =="TRUE" or str(row['Calculation basis unit']) =="1.0":
                calculationtype=3

            contact_Id=None
            for i in range(0, len(JsonResponse1)):
                if JsonResponse1[i]["IsSupplier"]:
                    if JsonResponse1[i]["Description"]==str(row['Payee']):
                        contact_Id=JsonResponse1[i]["ContactId"]
                        break

            liability_account=None
            if str(row["Liability account"]) != "nan":
                for j3 in range(0,len(account_data)):
                    if str(row["Liability account"]) == account_data[j3]['Name']:
                        if account_data[j3]['AccountType']==4:
                            liability_account=account_data[j3]["Id"]
                            break

            account = None
            if row["Expense account"] != "nan":
                for j3 in range(0, len(account_data)):
                    if str(row["Expense account"]) == account_data[j3]['Name']:
                        account = account_data[j3]["Id"]
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
            QuerySet["ExpenseAccountId"] =account
            QuerySet['Name'] = str(row['Company contribution item name'])
            QuerySet['Description'] = str(row['Description (optional)'])
            QuerySet['PayItemType'] = 7
         
            QuerySet['CalculationBasisType'] = calculationtype
            QuerySet['DefaultRate'] = default_rate
            QuerySet['LimitAmount'] = limit_amount
            QuerySet['IsPercentValue'] = "false"
            # QuerySet["IsDeductedForTax"]=str(row["Deduct from gross before calculating withholding"])
            QuerySet["PayeeId"]=contact_Id


            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
