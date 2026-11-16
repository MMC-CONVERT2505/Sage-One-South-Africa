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


def get_excel_invoice(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_invoice"]
        payload, base_url, headers = get_settings_myob(job_id)
        tax_url = f"{base_url}/GeneralLedger/TaxCode"
        taxresponse = requests.request("GET", tax_url, headers=headers, data=payload)
        taxJsonResponse = taxresponse.json()
        taxJsonResponse1 = taxJsonResponse["Items"]
        
        
        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        invoice_data = pd.read_excel(path, 'Invoice')

        
        job1 = dbname['job'].find({"job_id":job_id})
        job = []
        for i in job1:
            job.append(i) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        customer1 = dbname['customer'].find({"job_id":job_id})
        customer = []
        for i in customer1:
            customer.append(i) 

        item1 = dbname['item'].find({"job_id":job_id})
        item = []
        for i in item1:
            item.append(i) 

        for index, row in invoice_data.iterrows():
            date1=str(row['Transaction date']).split(" ")[0]
            date2=str(row['Due date']).split(" ")[0]
            balanceduedate = datetime.strptime(date2, "%Y-%m-%d")
            balanceduedate1=balanceduedate.strftime("%Y-%m-%d")
            transactiondate = datetime.strptime(date1, "%Y-%m-%d")
            transactiondate1=transactiondate.strftime("%Y-%m-%d")
            duedate = balanceduedate.date().day
            
            jobuid={}
            for i1 in range(0,len(job)):
                if job[i1]["Name"]==row['Job']:
                    jobuid["UID"]=job[i1]["UID"]
                    

            tax_code={}
            for i2 in range(0,len(taxJsonResponse1)):
                if row['Tax code']==taxJsonResponse1[i2]["Code"]:
                    tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                    break
                elif row['Tax code']==taxJsonResponse1[i2]["Description"]:
                    tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                    break
                else:
                    if taxJsonResponse1[i2]["Code"]=="N-T":
                        tax_code["UID"]=taxJsonResponse1[i2]["UID"]
            
            
            mainaccountuid={}
            for j1 in range(0,len(coa)):
                if str(row["Account No."]) == coa[j1]['DisplayId']:
                    mainaccountuid["UID"]=coa[j1]["UID"]

            customeruid={}
            for j2 in range(0,len(customer)):
                if row["Customer"] == customer[j2]['Company_Name']:
                    customeruid["UID"]=customer[j2]["UID"]
            
            itemuid={}
            for j3 in range(0,len(item)):
                if row["Item"] == item[j3]['Name']:
                    itemuid["UID"]=item[j3]["UID"]
            
            invoice_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error" : None,
                "Lines": [
                    {
                    "ShipQuantity": row["No. of Unit"],
                    "UnitPrice": round(row["Unit Price"],4),
                    "DiscountPercent":0 if math.isnan(row["Discount %"]) else float(row["Discount %"]),
                                
                    "Item": None if itemuid=={} else itemuid,
                    "Account": mainaccountuid,
                    "TaxCode": tax_code,
                    "Job": None if jobuid=={} else jobuid
                    }],
                    "Number": row["Invoice number"],
                    "Date": transactiondate1,
                    "Terms": {
                        "PaymentIsDue": "OnADayOfTheMonth",
                        "DueDate": balanceduedate1,
                        "BalanceDueDate": duedate
                    },
                    "IsTaxInclusive": False if row["Amounts are"] == 'Tax exclusive' else True  ,
                    "Customer": customeruid
                    }
    
            collection.insert_one(invoice_payload)


    except Exception as ex:
        traceback.print_exc()
        