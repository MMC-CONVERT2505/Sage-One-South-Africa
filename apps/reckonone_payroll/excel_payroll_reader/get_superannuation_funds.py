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


def get_excel_payroll_superannuation_funds(job_id, task_id):
    logging = log_config(job_id) 
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_payroll_superannuation_funds"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path, 'Superannuation funds')

        

        # payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        # book_Id=base_url[27:]
        # url = f"https://api-v2.reckonone.com/{book_Id}/superfundProviders"
        # response = requests.request("GET", url, headers=get_headers, data=payload)
        # logging.info(f"{job_id} get_payschedules_from_api--> url-->{url} response status-->{response.status_code}")
        # JsonResponse1 = response.json()
        # response_val=JsonResponse1["list"]
        
        
        instance_name = None
        for index, row in leave_data.iterrows():
            if str(row['Superannuation fund APRA Regulated'])=="False" or str(row['Superannuation fund APRA Regulated'])=="FALSE":
                
                QuerySet = {}
                electronic_addresses_data={}
                QuerySet['job_id'] = job_id
                QuerySet['task_id'] = task_id
                QuerySet['is_pushed'] = 0
                QuerySet['error'] = None
                QuerySet['payload'] = None

                email=""
                if str(row['Superannuation fund Self Managed Email address (optional)']) != "nan":
                    email= str(row['Superannuation fund Self Managed Email address (optional)'])
                else:
                    email=""

                bank_branch_number=""
                if str(row['Superannuation fund Self Managed BSB']) != "nan":
                    bank_branch_number= int(row['Superannuation fund Self Managed BSB'])
                else:
                    bank_branch_number=""
                
                bankBranchNumber=bank_branch_number

                bank_account_number=""
                if str(row['Superannuation fund Self Managed Account number']) != "nan":
                    bank_account_number= int(row['Superannuation fund Self Managed Account number'])
                else:
                    bank_account_number=""

                bankAccountNumber=bank_account_number

                QuerySet['name'] = str(row['Superannuation fund Self Managed Display name'])[:40]
                QuerySet['organisationName'] = str(row['Superannuation fund Self Managed Fund name'])[:40]
                print(len(QuerySet["name"]),"**************")

                branch_name=""
                if str(row['Superannuation fund Self Managed Branch Number (Optional)']) != "nan":
                    branch_name= str(row['Superannuation fund Self Managed Branch Number (Optional)'])
                else:
                    branch_name=""

                business_number=""
                if str(row['Superannuation fund Self Managed ABN (Optional)']) != "nan":
                    business_number= int(row['Superannuation fund Self Managed ABN (Optional)'])
                else:
                    business_number=""

                bank_details_name=""
                if str(row['Superannuation fund Self Managed Bank account name']) != "nan":
                    bank_details_name= str(row['Superannuation fund Self Managed Bank account name'])[:49]
                else:
                    bank_details_name=""

                QuerySet['branch']= branch_name
                QuerySet["businessNumber1"]= business_number
                bank_details={}
                bank_details["name"]=bank_details_name
                bank_details["bankBranchNumber"]=bankBranchNumber
                bank_details["bankAccountNumber"]=bankAccountNumber

                QuerySet["bankDetails"]=bank_details

                smsf={}
                smsf["fundName"]=str(row['Superannuation fund Self Managed Fund name'])[:49]
                smsf["electronicServiceAddress"]=str(row['Superannuation fund Self Managed Electronic service address (ESA)'])
                superfundDetails={"smsf":smsf}

                QuerySet["superfundDetails"]=superfundDetails

                QuerySet["status"]="Active"

                electronic_addresses_data["type"]="Email"
                electronic_addresses_data["address"]=email
                electronic_addresses=[electronic_addresses_data]
                QuerySet["electronicAddresses"]=electronic_addresses
            
            
                collection.insert_one(QuerySet)

            else:
                QuerySet = {}
                
                electronic_addresses_data={}
                super_fund_provider_details={}
                QuerySet['job_id'] = job_id
                QuerySet['task_id'] = task_id
                QuerySet['is_pushed'] = 0
                QuerySet['error'] = None
                QuerySet['payload'] = None

                email=""
                if str(row['Superannuation fund APRA Regulated Email address (optional)']) != "nan":
                    email= str(row['Superannuation fund APRA Regulated Email address (optional)'])
                else:
                    email=""

                employee_number=""
                if str(row['Superannuation fund APRA Regulated Employer number (Optional)']) != "nan":
                    employee_number= str(row['Superannuation fund APRA Regulated Employer number (Optional)'])
                else:
                    employee_number=""

                # super_fund_provider=None
                # for i in range(0, len(response_val)):
                #     if response_val[i]["name"]==str(row['Superannuation fund APRA Regulated Super Fund']):
                #         super_fund_provider=response_val[i]["id"]


                QuerySet['name'] = str(row['Superannuation fund APRA Regulated Display name'])
                QuerySet['organisationName'] = str(row['Superannuation fund APRA Regulated Super Fund'])

                electronic_addresses_data["type"]="Email"
                electronic_addresses_data["address"]=email
                electronic_addresses=[electronic_addresses_data]
                QuerySet["electronicAddresses"]=electronic_addresses

                # super_fund_provider_details["fund"]=super_fund_provider
                super_fund_provider_details["fund"]=str(row['Superannuation fund APRA Regulated Super Fund'])
                super_fund_provider_details["employerNumber"]=employee_number
                QuerySet["superfundDetails"]={"superfundProvider":super_fund_provider_details}
              
                collection.insert_one(QuerySet)

             

    except Exception as ex:
        traceback.print_exc()
