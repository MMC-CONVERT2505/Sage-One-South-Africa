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


def get_excel_payroll_allowance(job_id, task_id):
    print("inside get_excel_payroll_allowance")
    logging = log_config(job_id) 
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payrollallowance"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/',filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        allowance_data = pd.read_excel(path, 'Payitem Allowance')
        grouped_data = allowance_data
        account_data = list(dbname["reckon_coa"].find({"job_id":job_id}))

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/superitems"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_superitems_from_api--> url-->{url} response status-->{response.status_code}")
        JsonResponse2 = response.json()
        
       
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

            subtype_map = {
                    "Other": 26,
                    "Meals": 27,
                    "Transport": 28,
                    "Car": 29,
                    "Travel": 30,
                    "Laundry": 31,
                    "Cents per Kilometre":34,
                    "Tool Allowances":38,
                    "Domestic or Overseas Travel Allowances and Overseas Accommodation":37,
                    "Tasks":45,
                    "Overtime Meal Allowances":36,
                    "Award Transport Payments":35,
                    "Qualifications / Certificates":39,
                }
            
            sub_subtype_map = {
                    "General": 40,
                    "Home Office":44,
                    "Non Deductilble":41,
                    "Transport Or Fares":46,
                    "Private Vehicle":43,
                    "Uniform":42
                }

            calculationbasictype_map = {
                    "Quantity": 1,
                    "Hourly": 2,
                    "Other": 3

                }
            
            default_rates_map = {
                    "Per pay": 1,
                    "Per annum": 2,
                }



            if row["Allowance sub-type"] in subtype_map:
                SubTypeId = subtype_map[row["Allowance sub-type"]]
            else:
                SubTypeId = 0

            sub_subtype= None
            if row["Allowance Sub Sub-Type"] in sub_subtype_map:
                sub_subtype= sub_subtype_map[row["Allowance Sub Sub-Type"]]
            else:
                sub_subtype=None

            limittype=None
            if row['DEFAULT RATES (OPTIONAL) Limit Type'] in default_rates_map:
                limittype = default_rates_map[row["DEFAULT RATES (OPTIONAL) Limit Type"]]
            else:
                limittype = 0

            if row["Allowance type"] in payitemtype_map:
                payitemtype = payitemtype_map[row["Allowance type"]]
            else:
                payitemtype = 0

            account = None
            if row["Expense account"] != "nan":
                for j3 in range(0, len(account_data)):
                    if str(row["Expense account"]) == account_data[j3]['Name']:
                        account = account_data[j3]["Id"]
                        break

            limit_amount="0.01"
            if str(row['DEFAULT RATES (OPTIONAL) Limit'])=="nan" or str(row['DEFAULT RATES (OPTIONAL) Limit'])==" " or str(row['DEFAULT RATES (OPTIONAL) Limit'])=="0":
                limit_amount="0.01"
            else:
                limit_amount=str(row['DEFAULT RATES (OPTIONAL) Limit'])


            default_rate="0"
            if str(row["DEFAULT RATES (OPTIONAL) Default rate"])=="nan":
                default_rate="0"
            else:
                default_rate=str(row["DEFAULT RATES (OPTIONAL) Default rate"])


                    
            QuerySet['Name'] = str(row['Allowance item name'])
            QuerySet['PayItemType'] = 3
            QuerySet['SubTypeId'] = SubTypeId
            QuerySet["SubSubTypeId"] = sub_subtype
            # QuerySet['SubTypeName'] = str(row["Allowance sub-type"])
            # QuerySet['CalculationBasisType'] = calculationtype
            QuerySet['DefaultRate'] = default_rate
            QuerySet['LimitAmount'] = limit_amount
            QuerySet['LimitType'] = limittype
            QuerySet["Description"] = str(row["Description (optional)"])
            QuerySet["ExpenseAccountId"]=account
            # QuerySet["ExpenseAccountName"]=account_data[j3]['Name']
            QuerySet['IsPercentValue'] = False
            QuerySet['TaxApplicableName'] = str(row["Calculation method"])
            QuerySet["ShowAsAllowancePS"] = str(row["Show as allowance for STP"])
                        
            if row['Calculation basis Hourly'] == True:
                QuerySet['CalculationBasisType']=2          
            elif row['Calculation basis Fixed amount'] ==True:
                QuerySet['CalculationBasisType']=3
            elif row['Calculation basis unit'] ==True:
                QuerySet['CalculationBasisType']=1
            else:
                QuerySet['CalculationBasisType']=0
            
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

