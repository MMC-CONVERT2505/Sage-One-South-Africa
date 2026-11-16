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


def get_excel_Leave_balance(job_id, task_id):
   
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_leave_balance"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'Leave Balance')


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/ytds/leavebalances/headers"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        data=response.json()
        # print(data,"77777777777777777")

        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/payroll/contacts"
        response1 = requests.request("GET", url1, headers=get_headers, data=payload)
        data1=response1.json()
            
        
        
        instance_name = None


        for index, row in leave_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None            
            # QuerySet['list']= None
            
            for j in range(len(data1)):
                if data1[j]['Description'] == str(row['Description Name']).strip():
                    # print("match data")
                    emp_id=data1[j]['EmployeeId']
                    QuerySet['EmployeeId'] = data1[j]['EmployeeId']
                    QuerySet['EmployeeName'] = data1[j]['Description']
         

         
                    payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
                    url2 = f"{base_url}/payroll/contacts/{emp_id}"
                    response2 = requests.request("GET", url2, headers=get_headers, data=payload)
                    data2=response2.json()

                    for k in range(len(data2['EmployeeData']['Leaves'])):
                        if data2['EmployeeData']['Leaves'][k]['LeaveName'] == str(row['Leave Name 1']).strip():
                            QuerySet['PayItemId'] = data2['EmployeeData']['Leaves'][k]['PayItemsLeavesId']
                            QuerySet['PayItem'] = data2['EmployeeData']['Leaves'][k]['LeaveName']
                            QuerySet['PayItemSubtypeId'] = data2['EmployeeData']['Leaves'][k]['PayItemTypeId']
                            break
                    break     

            for i in range(len(data)):
                if data[i]['TypeId'] == 2 and data[i]['Reference'] == "PAYROLL_APP_LEAVE":
                    HeaderId=data[i]['Id']
                    QuerySet['HeaderId'] = data[i]['Id']
                    break

            QuerySet['Quantity'] = str(row['Quantity (hours) 1']).strip()
            QuerySet['EffectiveDate'] = str(datetime.now())[:-4:]

            # if not math.isnan(row['Quantity (hours) 1']) and row['Quantity (hours) 1'] != "":
                # QuerySet['QuerySet1'] = QuerySet1
                # list.append(QuerySet)


            # print(QuerySet)
            collection.insert_one(QuerySet)


    except Exception as ex:
        traceback.print_exc()
