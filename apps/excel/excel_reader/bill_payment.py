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



def get_excel_bill_payment(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_bill_payment"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        billpayment_data = pd.read_excel(path, 'Supplier Payment')

        all_bill1 = dbname['all_bill'].find({"job_id":job_id})
        all_bill_data = []
        for i in all_bill1:
            all_bill_data.append(i) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        supplier1 = dbname['supplier'].find({"job_id":job_id})
        supplier = []
        for i in supplier1:
            supplier.append(i) 

        instance_name=None
        for index, row in billpayment_data.iterrows():
            date1=str(row['Date']).split(" ")[0]
            transactiondate = datetime.strptime(date1, "%Y-%m-%d")
            transactiondate1=transactiondate.strftime("%Y-%m-%d")
            
            mainaccountuid={}
            for j1 in range(0,len(coa)):
                if str(row["Bank account"]) == str(coa[j1]['DisplayId']):
                    mainaccountuid["UID"]=coa[j1]["UID"]

            billuid={}
            for j2 in range(0,len(all_bill_data)):
                if str(row["Bill Number"]) == str(all_bill_data[j2]['supplier_invoice_no']):
                    billuid["UID"]=all_bill_data[j2]["UID"]
                    break
                elif str(row["Bill Number"]) == str(all_bill_data[j2]['invoice_no']):
                    billuid["UID"]=all_bill_data[j2]["UID"]
                    break
                elif str(row["Bill Number"])[-13:]== str(all_bill_data[j2]['invoice_no'][-13:]):
                    billuid["UID"]=all_bill_data[j2]["UID"]
                    break
                
            supplieruid={}
            for j3 in range(0,len(supplier)):
                if row["Supplier"] == supplier[j3]['CompanyName']:
                    supplieruid["UID"]=supplier[j3]["UID"]
                    break
                # elif supplier[j3]['CompanyName'].startswith(row["Supplier"]) and supplier[j3]['CompanyName'].endswith("- S") :
                #     supplieruid["UID"]=supplier[j3]["UID"]
                #     break
            
            
            billpayment_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error":None,
                "payload":None,
                "PayFrom": "Account",
                "Account": mainaccountuid,
                "Supplier": supplieruid,
                "BillNumber" : str(row["Bill Number"]),
                "PaymentNumber": str(row["Reference number"])[0:13],
                "Date": transactiondate1,
                "AmountPaid": row["Amount Paid"],
                "Memo": instance_check(instance_name,row["Description of transaction"]),
                "Lines": [
                {
                "Type": "Bill",
                "Purchase": billuid if billuid!={} else None,
                "AmountApplied": row["Amount Paid"]
                }
                ]
            }
            collection.insert_one(billpayment_payload)


    except Exception as ex:
        traceback.print_exc()
        