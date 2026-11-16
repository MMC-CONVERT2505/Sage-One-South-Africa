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


def get_excel_ytds_Fringe_benefits(job_id, task_id):
   
    try:
        dbname = get_mongodb_database()
        collection = dbname["get_excel_ytds_Fringe_benefits"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'YTDS Fringe benefits')


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url = f"{base_url}/payroll/ytds/stpbalances/headers"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        data=response.json()


        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
        url1 = f"{base_url}/payroll/contacts"
        response1 = requests.request("GET", url1, headers=get_headers, data=payload)
        data1=response1.json()
            
        
        instance_name = None

        Category_INB_map = {

                        "Reportable fringe benefit amount (non-exempt)": 5,
                        "Reportable fringe benefit amount (exceeding exempt)": 26,
                        
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

           
            for i in range(len(data)):
                if data[i]['TypeId'] == 3 and data[i]['Reference'] == "PAYROLL_APP_INB":
                    HeaderId=data[i]['Id']
                    QuerySet['HeaderId'] = data[i]['Id']
                    break
                
                else:
                    QuerySet['HeaderId'] =None


            QuerySet['TypeId']= 1

            Stp_category= None
            if str(row["STP reporting category"]).strip() in Category_INB_map:
                Stp_category = Category_INB_map[str(row["STP reporting category"]).strip()]
                QuerySet['CategoryId'] = Stp_category
                QuerySet['CategoryName'] = str(row["STP reporting category"]).strip()

            else:
                QuerySet['CategoryId'] = None

       
            QuerySet['Amount'] = row['Gross amount (YTD)']
            QuerySet['EffectiveDate'] = date_convert(row['Effective date'])


          
            collection.insert_one(QuerySet)
        
        


    except Exception as ex:
        traceback.print_exc()
