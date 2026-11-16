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


def get_excel_reckon_bill_payment(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_bill_payment"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        bankpayment_data = pd.read_excel(path, 'Supplier Payment')

        all_invoice1 = dbname['reckon_bill'].find({"job_id":job_id})
        all_bill_data = []
        for i3 in all_invoice1:
            all_bill_data.append(i3) 

        coa1 = dbname['reckon_bank_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2)

        reckoncoa1 = dbname['reckon_coa'].find({"job_id":job_id})
        reckoncoa = []
        for i2 in reckoncoa1:
            reckoncoa.append(i2) 

        customer1 = dbname['reckon_contact'].find({"job_id":job_id})
        customer = []
        for i1 in customer1:
            customer.append(i1) 
   
        instance_name=None
        for index, row in bankpayment_data.iterrows():

            # date2=str(row["Date"]).split(" ")[0]
            # date = datetime.strptime(date2, "%Y-%m-%d")
            # date1=date.strftime("%Y-%m-%d")

            AccountsPayableCategoryId = None
            for j11 in range(0,len(reckoncoa)):
                if reckoncoa[j11]['Name'] == "Accounts Payable":
                    AccountsPayableCategoryId=reckoncoa[j11]["Id"]
                    break

            mainaccountuid=None
            for j1 in range(0,len(coa)):
                if str(row["Bank account Name"]) == coa[j1]['BankName']:
                    mainaccountuid=coa[j1]["BankAccountID"]
                    print(mainaccountuid)
                    break
                
            billid=None
            contactid=None
            balance=0
            for j2 in range(0,len(all_bill_data)):
                print(str(row["Bill Number"]),str(all_bill_data[j2]['Reference']))
                if str(row["Bill Number"]) == str(all_bill_data[j2]['Reference']):
                    print(True)
                    billid=all_bill_data[j2]["Id"]
                    contactid = all_bill_data[j2]["CustomerID"]
                    balance = all_bill_data[j2]["Balance"]
                    break
                else:
                    print("not match")
            
          
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
                "ContactName": contactid,
                "AllocateFullAmount":False if instance_check(instance_name,row['Amount'])!=balance else True,
                "Reference": instance_check(instance_name,row['Reference']),
                "AccountsPayableCategoryId": AccountsPayableCategoryId,
                "Narration": instance_check(instance_name,row['Details']),
                "Allocations": [
                    {
                    "AllocationAmount":instance_check(instance_name,row['Amount']),
                    "AllocationTypeId":2,
                    "AllocationType": "Bill",
                    "RefId": billid
                    }
                ],
                "AllocationSplit":[]
                }
            
            collection.insert_one(invoicepayment_payload)


    except Exception as ex:
        traceback.print_exc()
        