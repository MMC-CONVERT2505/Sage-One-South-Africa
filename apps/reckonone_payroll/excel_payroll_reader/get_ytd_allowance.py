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
import requests
from apps.util.qbo_util import date_convert


def get_excel_ytds_allowance(job_id, task_id):
   
    try:
        dbname = get_mongodb_database()
        collection = dbname["get_excel_ytds_allowance"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'YTDS Allowance')


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/ytds/grosspays/headers"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        data=response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/payroll/contacts"
        response1 = requests.request("GET", url1, headers=get_headers, data=payload)
        data1=response1.json()
            

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url2 = f"{base_url}/payroll/payrollitems/500"
        response2 = requests.request("GET", url2, headers=get_headers, data=payload)
        data2=response2.json()
        
        filtered_records = [item for item in data2['Items'] if item['PayItemTypeName'] == "Allowance"]

        # print(filtered_records)
    
        
        instance_name = None

        Category_INB_map = {
                        "Gross payment": 3,
                        "CDEP payment": 4,
                        "Reportable fringe benefit amount (non-exempt)": 5,
                        "Reportable fringe benefit amount (exceeding exempt)": 26,
                        "Reportable employer superannuation contribution": 6,
                        "Deductible amount of the undeducted purchase price on an annuity": 7,
                        "Lump sum A - R" : 9,
                        "Lump sum A - T1": 10,
                        "Lump sum B": 11,
                        "Lump sum D": 12,
                        "Lump sum E": 13,
                        "Exempt foreign employment income": 25,
                        "Allowance": 14,
                        "Union/Professional association fee": 15,
                        "Workplace giving": 16,
                        "OvertimePayment": 27,
                        "BonusOrCommission": 28,
                        "DirectorsFee": 29,
                        "LumpSumW": 30,
                        "SalarySacrificeSuperannuation": 31,
                        "SalarySacrificeOtherEmployeeBenefits": 32,
                        "CashOutOfLeaveInService": 33,
                        "UnusedLeaveOnTermination": 34,
                        "PaidParentalLeave": 35,
                        "WorkersCompensation": 36,
                        "AncillaryAndDefenceLeave": 37,
                        "OtherPaidLeave":38
                }
                    
        Category_ETP_map = {

                        "R": 17,
                        "O": 18,
                        "S": 19,
                        "P": 20,
                        "D": 21,
                        "B": 22,
                        "N": 23
                    }

        income_type_id ={
                        "Salary and wages" : 1,
                        "Working holiday maker": 2,
                        "Seasonal worker program": 3,
                        "Closely held payees": 4,
                        "Voluntary agreement":5
        }

        Tax_ETP_map = {
                        "Taxable": 1,
                        "Tax free": 2
        }

        for index, row in leave_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None            
            


            for j in range(len(data1)):
                if data1[j]['Description'] == str(row['Description Name']).strip():
                    # print("match data")
                    emp_id=data1[j]['EmployeeId']
                    QuerySet['EmployeeId'] = data1[j]['EmployeeId']
                    QuerySet['EmployeeName'] = data1[j]['Description']
                    break

            for k in range(len(filtered_records)):
                if filtered_records[k]['FullName'] == str(row['Allowances item name']).strip():
                    QuerySet['PayItemId'] = filtered_records[k]['Id']
                    QuerySet['PayItem'] = filtered_records[k]['FullName']
                    QuerySet['PayItemSubtypeId'] = filtered_records[k]['SubTypeId']
                    break
                else:
                    QuerySet['PayItemId'] = None
                    QuerySet['PayItem'] = None


            for i in range(len(data)):
                if data[i]['TypeId'] == 1 and data[i]['Reference'] == "PAYROLL_APP_PAY":
                    HeaderId=data[i]['Id']
                    QuerySet['HeaderId'] = data[i]['Id']
                    break
                else:
                    QuerySet['HeaderId'] = None
            
            if row['INB'] == True:
                QuerySet['TypeId']= 1

                Stp_category= None
                if str(row["STP reporting category"]).strip() in Category_INB_map:
                    Stp_category = Category_INB_map[str(row["STP reporting category"]).strip()]
                    QuerySet['CategoryId'] = Stp_category

                else:
                    QuerySet['CategoryId'] = None


            elif row['ETP'] == True:
                QuerySet['TypeId']= 2

                Stp_category2= None
                if str(row["STP reporting category"]).strip() in Category_ETP_map:
                    Stp_category2 = Category_ETP_map[str(row["STP reporting category"]).strip()]
                    QuerySet['CategoryId'] = Stp_category2
                

                ETP_tax= None
                if str(row["ETP tax component"]).strip() in Tax_ETP_map:
                    ETP_tax = Tax_ETP_map[str(row["ETP tax component"]).strip()]
                    QuerySet['EtpDetailTypeId'] = ETP_tax
                
                else:
                    QuerySet['EtpDetailTypeId'] = None


            elif row['ETP'] == False and row['INB'] == False:
                QuerySet['EtpDetailTypeId'] = None
                QuerySet['CategoryId'] = None   

            elif row['ETP'] == "nan" and row['INB'] == "nan":
                QuerySet['EtpDetailTypeId'] = None
                QuerySet['CategoryId'] = None   

            else:
                QuerySet['TypeId']= 0
                QuerySet['EtpDetailTypeId'] = None
                QuerySet['CategoryId'] = None   


            income_type= None
            if str(row["Income type"]).strip() in income_type_id:
                income_type = income_type_id[str(row["Income type"]).strip()]
                QuerySet['IncomeTypeId'] = income_type
            else:
                QuerySet['IncomeTypeId'] = None



            QuerySet['Amount'] = row['Gross amount (YTD)']
            QuerySet['EffectiveDate'] = date_convert(row['Effective date'])


            # if QuerySet['PayItemId'] != "nan" and QuerySet['PayItemId'] != "":
            collection.insert_one(QuerySet)
        


    except Exception as ex:
        traceback.print_exc()
