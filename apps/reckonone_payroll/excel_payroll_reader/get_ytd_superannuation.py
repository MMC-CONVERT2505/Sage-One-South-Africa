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
from apps.util.qbo_util import instance_check,date_convert
import requests


def get_excel_ytds_superannuation(job_id, task_id):
   
    try:
        dbname = get_mongodb_database()
        collection = dbname["get_excel_ytds_superannuation"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'YTDS Superannuation')


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/ytds/grosspays/headers"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        data=response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/payroll/contacts"
        response1 = requests.request("GET", url1, headers=get_headers, data=payload)
        data1=response1.json()
        # print(data1)
            

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url2 = f"{base_url}/payroll/superitems/200"
        response2 = requests.request("GET", url2, headers=get_headers, data=payload)
        data2=response2.json()
        print(len(data2))
        

        # payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        # book_Id=base_url[27:]
        # url3 = f"https://api-v2.reckonone.com/{book_Id}/superfundProviders?page=1&perpage=500"
        # response3 = requests.request("GET", url3, headers=get_headers, data=payload)
        # data3=response3.json()
        # filter1=str(row['Fund product'])
        # string = str(row['Fund product'])
        # string_list = string.split()
        # print(string_list)
        # filtered_records = [item for item in data3['list'] if item['name'] == string_list[0]]



        filtered_records =data2['Items']
    
        
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
            

            payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
            book_Id=base_url[27:]
            url3 = f"https://api-v2.reckonone.com/{book_Id}/superfundProviders?page=1&perpage=500"
            response3 = requests.request("GET", url3, headers=get_headers, data=payload)
            data3=response3.json()
            string = str(row['Fund product'])
            string_list = string.split()
            # filtered_records1 = [item for item in data3['list'] if item['name'].startswith(string_list[0])]
            for item in data3['list']:
                if item['name'].startswith(string[:7]):
                    # print(item['name'],"********")
                    id1=item['id']
                    payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
                    book_Id1=base_url[27:]
                    url4 = f"https://api-v2.reckonone.com/{book_Id1}/superfundProviders/{id1}/products"
                    response4 = requests.request("GET", url4, headers=get_headers, data=payload)
                    data4=response4.json()
                    # print(data4['list'],"***********")
                    for j in range(len(data4['list'])):
                        if data4['list'][j]['name'] == str(row['Fund product']):
                            # print("match the superfund product",data4['list'][j]['name'],data4['list'][j]['id'])
                            QuerySet['SuperFundProductId'] = data4['list'][j]['id']
                            QuerySet['SuperFundProductName'] = data4['list'][j]['name']
                            break
                        else:
                            QuerySet['SuperFundProductId'] = None
                            QuerySet['SuperFundProductName'] = None
                    break

                else:
                            QuerySet['SuperFundProductId'] = None
                            QuerySet['SuperFundProductName'] = None


            

            for j in range(len(data1)):
                if data1[j]['Description'] == str(row['Description Name']).strip():
                    # print("match data name")
                    QuerySet['EmployeeId'] = data1[j]['EmployeeId']
                    QuerySet['EmployeeName'] = data1[j]['Description']
                    QuerySet['EmploymentType'] = data1[j]['EmploymentType']
                    break
                
                else:

                    QuerySet['EmployeeId'] = None
                    QuerySet['EmploymentType'] = None



            for k in range(len(filtered_records)):
                if filtered_records[k]['Name'] == str(row['Superannuation item name']).strip():
                    QuerySet['PayItemId'] = filtered_records[k]['PayItemId']
                    QuerySet['PayItemTypeId'] = filtered_records[k]['PaySubType']
                    QuerySet['PayItemTypeRoot'] = filtered_records[k]['PayItemType']
                    break
                else:
                    QuerySet['PayItemId'] = None
                    QuerySet['PayItemTypeId'] = None
                    QuerySet['PayItemTypeRoot'] = None

            for i in range(len(data)):
                if data[i]['TypeId'] == 1 and data[i]['Reference'] == "PAYROLL_APP_PAY":
                    HeaderId=data[i]['Id']
                    QuerySet['HeaderId'] = data[i]['Id']
                    break


            income_type= None
            if str(row["Income type"]).strip() in income_type_id:
                income_type = income_type_id[str(row["Income type"]).strip()]
                QuerySet['IncomeTypeId'] = income_type
            else:
                QuerySet['IncomeTypeId'] = None


            QuerySet['Amount'] = row['Gross amount (YTD)']
            QuerySet['EffectiveDate'] = date_convert(row['Effective date'])

            collection.insert_one(QuerySet)
            # print(QuerySet)
        


    except Exception as ex:
        traceback.print_exc()
