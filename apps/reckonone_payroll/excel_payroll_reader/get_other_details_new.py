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

def get_excel_payroll_other_details(job_id, task_id):
    
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_other_details"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0, len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        leave_data = pd.read_excel(path,'Other details')

    

        for index, row in leave_data.iterrows():
            QuerySet = {}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            QuerySet['Payments']=None
            QuerySet["employee_id"] = str(row['Employee Id'])
            
            Payment=[]
            QuerySet1={}

            if row['Bank Details'] == True:
                
                if row[f'Bank Details Payment Type Electronic funds transfer (EFT)']=="Electronic funds transfer (EFT)":
                    QuerySet1['TypeId'] = 1
                elif row[f'Bank Details Payment Type Electronic funds transfer (EFT)']== "cash":
                    QuerySet1['TypeId'] = 2 

                if  QuerySet1['TypeId'] == 1:
                    QuerySet1['AmountTypeId'] = 1
                    QuerySet1['AccountName'] = str(row['Account name'])
                    QuerySet1['Bsb'] = str(row[f'BSB'])
                    QuerySet1['BankName'] = str(row['Financial institution'])
                    QuerySet1['AccountNumber'] = int(row['Account number'])
                    QuerySet1['Reference'] = str(row['Reference'])
                    # QuerySet1['Amount'] = int(row['Pay amount'])
                    Payment.append(QuerySet1)
                
                elif QuerySet1['TypeId'] == 2:
                    QuerySet1['AmountTypeId'] = 1
                    QuerySet1['Reference'] = str(row[f'Reference'])
                    QuerySet1['Amount'] = int(row[f'Pay amount'])
                    Payment.append(QuerySet1)
               

            QuerySet2={}

            if row['FIXED DOLLAR ALLOCATION'] == True and row['Bank Details'] == True:
                    
                if row[f'DOLLAR Details Payment Type Electronic funds transfer (EFT)']=="Electronic funds transfer (EFT)":
                    QuerySet2['TypeId'] = 1
                elif row[f'DOLLAR Details Payment Type Electronic funds transfer (EFT)']== "cash":
                    QuerySet2['TypeId'] = 2 

                if  QuerySet2['TypeId'] == 1:
                    QuerySet2['AmountTypeId'] = 2
                    QuerySet2['AccountName'] = str(row['DOLLAR Account name'])
                    QuerySet2['Bsb'] = str(row['DOLLAR BSB'])
                    QuerySet2['BankName'] = str(row['DOLLAR Financial institution'])
                    QuerySet2['AccountNumber'] = int(row['DOLLAR Account number'])
                    QuerySet2['Reference'] = str(row['DOLLAR Reference'])
                    QuerySet2['Amount'] = int(row['DOLLAR Pay amount'])
                    Payment.append(QuerySet2)
                    
                elif QuerySet2['TypeId'] == 2:
                    QuerySet2['AmountTypeId'] = 2
                    QuerySet2['Reference'] = str(row[f'DOLLAR Reference'])
                    QuerySet2['Amount'] = int(row[f'DOLLAR Pay amount'])
                    Payment.append(QuerySet2)

            QuerySet3={}

            if row['PERCENTAGE ALLOCATION'] == True and row['Bank Details'] == True:
                    
                if row[f'PERCENTAGE Details Payment Type Electronic funds transfer (EFT)']=="Electronic funds transfer (EFT)":
                    QuerySet3['TypeId'] = 1
                elif row[f'PERCENTAGE Details Payment Type Electronic funds transfer (EFT)']== "cash":
                    QuerySet3['TypeId'] = 2 

                if  QuerySet3['TypeId'] == 1:
                    QuerySet3['AmountTypeId'] = 3
                    QuerySet3['AccountName'] = str(row['PERCENTAGE Account name'])
                    QuerySet3['Bsb'] = str(row['PERCENTAGE BSB'])
                    QuerySet3['BankName'] = str(row['PERCENTAGE Financial institution'])
                    QuerySet3['AccountNumber'] = int(row['PERCENTAGE Account number'])
                    QuerySet3['Reference'] = str(row['PERCENTAGE Reference'])
                    QuerySet3['Amount'] = int(row['PERCENTAGE Pay amount'])
                    Payment.append(QuerySet3)
                    
                elif QuerySet3['TypeId'] == 2:
                    QuerySet3['AmountTypeId'] = 3
                    QuerySet3['Reference'] = str(row[f'PERCENTAGE Reference'])
                    QuerySet3['Amount'] = int(row[f'PERCENTAGE Pay amount'])
                    Payment.append(QuerySet3)



            QuerySet['Payments']=Payment
            collection.insert_one(QuerySet)



    except Exception as ex:
        traceback.print_exc()

