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



def get_excel_invoice_payment(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_invoice_payment"]
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        invoicepayment_data = pd.read_excel(path, 'Customer payment')

        all_invoice1 = dbname['all_invoice'].find({"job_id":job_id})
        all_invoice_data = []
        for i3 in all_invoice1:
            all_invoice_data.append(i3) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2) 

        customer1 = dbname['customer'].find({"job_id":job_id})
        customer = []
        for i1 in customer1:
            customer.append(i1) 
   
        instance_name=None
        for index, row in invoicepayment_data.iterrows():

            date2=str(row["Date"]).split(" ")[0]
            date = datetime.strptime(date2, "%Y-%m-%d")
            date1=date.strftime("%Y-%m-%d")
            mainaccountuid={}
            for j1 in range(0,len(coa)):
                if 'DisplayId' in coa[j1]:
                    if str(row["Bank account"]) == coa[j1]['DisplayId']:
                        mainaccountuid["UID"]=coa[j1]["UID"]

            invoiceuid={}
            customeruid={}
            for j2 in range(0,len(all_invoice_data)):
                if str(row["Invoice number"]) == str(all_invoice_data[j2]['Invoice_Number']):
                    invoiceuid["UID"]=all_invoice_data[j2]["UID"]
                    customeruid["UID"]=all_invoice_data[j2]["Customer_ID"]
                    break
                elif str(row["Invoice number"]) == str(all_invoice_data[j2]['Customer_po_number']):
                    invoiceuid["UID"]=all_invoice_data[j2]["UID"]
                    customeruid["UID"]=all_invoice_data[j2]["Customer_ID"]
                    break
            
            
            # customeruid={}
            # for j3 in range(0,len(customer)):
            #     if row["Customer"] == customer[j3]['Company_Name']:
            #         customeruid["UID"]=customer[j3]["UID"]
            
            invoicepayment_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "PayFrom": "Account",
                "Account": mainaccountuid,
                "Customer": customeruid,
                "invnumber":instance_check(instance_name,row["Invoice number"]),
                "ReceiptNumber": str(row["Reference number"])[0:13],
                "Date": date1,
                "AmountPaid": instance_check(instance_name,row["Amount received"]),
                "Memo": instance_check(instance_name,row["Description of transaction"]),
                "Invoices": [
                    {
                    "UID":invoiceuid['UID'] if invoiceuid!= {} else {},
                    "AmountApplied": instance_check(instance_name,row["Amount received"]),
                    "Type": "Invoice"
                    }
                ]}
            collection.insert_one(invoicepayment_payload)


    except Exception as ex:
        traceback.print_exc()
        