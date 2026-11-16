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
        superannuation_data = pd.read_excel(path, 'Pay Item Superannuation')
        grouped_data = superannuation_data

        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))
         

        instance_name = None
        for index, row in superannuation_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
           
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
            for j3 in range(0,len(account_data)):
                if str(row["Expense account"]) == account_data[j3]['Name']:
                    account=account_data[j3]["Id"]
                    
            paysubtype=0
            if str(row["Superannuation type"]) in paysubtype_map:
                paysubtype = paysubtype_map[str(row["Superannuation type"])]
            else:
                paysubtype = 0
            
            IsSR_val=False
            if str(row['Rate basis Statutory rate'])=="True" or str(row['Rate basis Statutory rate'])=="TRUE" or str(row['Rate basis Statutory rate'])=="1.0":
                IsSR_val=True
            else:
                IsSR_val=False

            default_rate=0
            if str(row['IsPercentValue'])=="True" or str(row['IsPercentValue'])=="TRUE" or str(row['IsPercentValue'])=="1.0":
                default_rate=str(row["Default rate in (%)"])
            else:
                default_rate=str(row["Default rate in ($)"])

            
            Is_percent_value=False
            if str(row["IsPercentValue"]) =="True" or str(row["IsPercentValue"]) =="TRUE" or str(row["IsPercentValue"]) =="1.0":
                Is_percent_value=True
            else:
                Is_percent_value=False

            deduct_gross_before_tax_value=False
            if str(row['Deduct from gross before calculating tax']) =="True" or str(row["Deduct from gross before calculating tax"]) =="TRUE" or str(row["Deduct from gross before calculating tax"]) =="1.0":
                deduct_gross_before_tax_value=True
            else:
                deduct_gross_before_tax_value=False

            threshold_amount=None
            if str(row['Threshold amount'])!="nan":
                threshold_amount = str(row['Threshold amount'])
            else:
                threshold_amount = None

            
            if paysubtype ==23 or  paysubtype ==24 or  paysubtype ==25:
                QuerySet['PaySubType'] = paysubtype
                QuerySet["PayItemType"]=6
                QuerySet['Name'] = str(row['Superannuation item name'])
                QuerySet['Description'] = str(row['Description'])
                QuerySet["ExpenseAccountId"]=None
                QuerySet["ThresholdAmount"]=None
                QuerySet["IsPercentValue"]=Is_percent_value
                QuerySet['IsSR'] = False
                QuerySet["DefaultRate"]=default_rate
                QuerySet["Minimum"]=str(row['Minimum'])
                QuerySet["Limit"]= str(row['Limit per pay'])
                QuerySet["DeductGrossBeforeTax"]=deduct_gross_before_tax_value
            


            if paysubtype == 19 or paysubtype == 22 :
                QuerySet['PaySubType'] = paysubtype
                QuerySet["PayItemType"]=6
                QuerySet['Name'] = str(row['Superannuation item name'])
                QuerySet['Description'] = str(row['Description'])
                QuerySet["ExpenseAccountId"]=account
                QuerySet["ThresholdAmount"]=threshold_amount
                if threshold_amount!=None:
                    QuerySet["UseStatutoryThreshold"]=False
                QuerySet["IsSR"]=IsSR_val
                
                # if str(row['Rate basis Statutory rate'])!="True" or str(row['Rate basis Statutory rate'])!="TRUE" or str(row['Rate basis Statutory rate'])!="1.0":
                if str(row['Rate basis Statutory rate']) not in ["True", "TRUE", "1.0"]:
                    QuerySet["DefaultRate"]=default_rate
                    QuerySet["IsPercentValue"]=Is_percent_value

                

            if paysubtype == 20 or paysubtype == 21:
                QuerySet['PaySubType'] = paysubtype
                QuerySet["PayItemType"]=6
                QuerySet['Name'] = str(row['Superannuation item name'])
                QuerySet['Description'] = str(row['Description'])
                QuerySet['IsSR'] = False
                QuerySet["IsPercentValue"]=Is_percent_value
                QuerySet["DefaultRate"]=default_rate
                QuerySet["ExpenseAccountId"]=account
               
            
            

            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
