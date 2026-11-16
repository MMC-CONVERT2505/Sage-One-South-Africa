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
from apps.util.qbo_util import instance_check


def get_excel_reckon_invoice_payment(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_invoice_payment"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        invoicepayment_data = pd.read_excel(path, 'Customer payment')

        all_invoice1 = dbname['reckon_invoice'].find({"job_id":job_id})
        all_invoice_data = []
        for i3 in all_invoice1:
            all_invoice_data.append(i3) 

        coa1 = dbname['reckon_bank_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2)

        reckoncoa = dbname['reckon_coa'].find({"job_id":job_id})
        reckoncoa1 = []
        for i2 in reckoncoa:
            reckoncoa1.append(i2) 

        customer1 = dbname['reckon_contact'].find({"job_id":job_id})
        customer = []
        for i1 in customer1:
            customer.append(i1) 
   
        instance_name=None
        for index, row in invoicepayment_data.iterrows():

            # date2=str(row["Date"]).split(" ")[0]
            # date = datetime.strptime(date2, "%Y-%m-%d")
            # date1=date.strftime("%Y-%m-%d")

            AccountsReceivableCategoryId = None
            for j11 in range(0,len(reckoncoa1)):
                if reckoncoa1[j11]['Name'] == "Accounts Receivable":
                    AccountsReceivableCategoryId=reckoncoa1[j11]["Id"]
                    break

            mainaccountuid=None
            for j1 in range(0,len(coa)):
                if str(row["Bank account Name"]) == coa[j1]['BankName']:
                    mainaccountuid=coa[j1]["BankAccountID"]
                    break
                # elif str(row["Bank account Code"]) == coa[j1]['AccountCode']:
                #     mainaccountuid=coa[j1]["BankAccountID"]
                #     break

            invoiceid=None
            contactid=None
            balance=0
            for j2 in range(0,len(all_invoice_data)):
                if str(row["Invoice Number"]) == str(all_invoice_data[j2]['Reference']):
                    print(True)
                    invoiceid=all_invoice_data[j2]["Id"]
                    contactid = all_invoice_data[j2]["CustomerID"]
                    balance = all_invoice_data[j2]["Balance"]
                    break
                
            invoicepayment_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "TransDate": str(row["Date"]),
                "Amount": instance_check(instance_name,row['Amount']),
                "BankAccountId": mainaccountuid,
                "ContactId": contactid,
                "AllocateFullAmount":False if instance_check(instance_name,row['Amount'])!=balance else True,
                "Reference": instance_check(instance_name,row['Reference']),
                "AccountsReceivableCategoryId":AccountsReceivableCategoryId,
                "Narration": instance_check(instance_name,row['Details']),
                "Allocations": [
                    {
                    "AllocationAmount":instance_check(instance_name,row['Amount']),
                    "AllocationTypeId":1,
                    "RefId": invoiceid
                    }
                ],
                "AllocationSplit":[]
                }
            
            collection.insert_one(invoicepayment_payload)


    except Exception as ex:
        traceback.print_exc()
        