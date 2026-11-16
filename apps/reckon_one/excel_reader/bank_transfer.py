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
from apps.util.qbo_util import instance_check


def get_excel_reckon_bank_transfer(job_id,task_id):
    try:

        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_bank_transfer"]
        
        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory)
                        if f.startswith(file_prefix)), None)
        if filename is None:
            return
        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        bank_transfer_data = pd.read_excel(path, 'Bank Transfer')

        
        reckon_bank_account1 = dbname["reckon_bank_account"].find({"job_id":job_id})
        reckon_bank_account = []
        for p1 in reckon_bank_account1:
            reckon_bank_account.append(p1) 

        
        instance_name=None
        
        for index, row in bank_transfer_data.iterrows():
            
            date=str(row["Date"]).split(" ")[0]
            stdate = datetime.strptime(date, "%Y-%m-%d")
            date1=stdate.strftime("%Y-%m-%d")
            

            fromaccountuid=None
            for a1 in range(0,len(reckon_bank_account)):
                if str(row["Transfer from"]).replace(":","-") == reckon_bank_account[a1]['BankName'].replace(":","-"):
                    fromaccountuid=reckon_bank_account[a1]["BankAccountID"]
                

            toaccountuid=None
            for a11 in range(0,len(reckon_bank_account)):
                if str(row["Transfer to"]).replace(":","-") == reckon_bank_account[a11]['BankName'].replace(":","-"):
                    toaccountuid=reckon_bank_account[a11]["BankAccountID"]
                    
                    
            banktransfer_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": "",
                "payload": "",
                "FromBankAccountId": fromaccountuid,
                "ToBankAccountId":  toaccountuid,
                "FromReconciliationStatus":0,
                "ToReconciliationStatus":0,
                "TransferDate": date1,
                "Description":instance_check(instance_name,row['Description']),
                "Amount" :instance_check(instance_name,row['Amount']),
                }
            collection.insert_one(banktransfer_payload)


    except Exception as ex:
        traceback.print_exc()
        