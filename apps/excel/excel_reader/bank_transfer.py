import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl
from datetime import datetime
import math

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path


def get_excel_bank_transfer(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_bank_transfer"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
      
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        banktransfer_data = pd.read_excel(path, 'Bank Transfer')

        
        x = dbname['chart_of_account'].find({"job_id":job_id})
        arr = []
        for i in x:
            arr.append(i) 

        for index, row in banktransfer_data.iterrows():
            
            date=str(row["Date"]).split(" ")[0]
            stdate = datetime.strptime(date, "%Y-%m-%d")
            date1=stdate.strftime("%Y-%m-%d")

            fromaccountuid={}
            toaccountuid={}
            for a1 in range(0,len(arr)):
                if str(row["Bank account from"]) == arr[a1]['DisplayId']:
                    fromaccountuid["UID"]=arr[a1]["UID"]
                    break
            for a2 in range(0,len(arr)):
                if str(row["Bank account to"]) == arr[a2]['DisplayId']:
                    toaccountuid["UID"]=arr[a2]["UID"]
                    break
                    
            banktransfer_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": "",
                "payload": "",
                "FromAccount": fromaccountuid,
                "ToAccount":  toaccountuid,
                "TransferNumber": row["Reference number"],
                "Date": date1,
                "Amount": row["Amount"],
                "Memo": row["Description of transaction"],
                }
            collection.insert_one(banktransfer_payload)


    except Exception as ex:
        traceback.print_exc()
        