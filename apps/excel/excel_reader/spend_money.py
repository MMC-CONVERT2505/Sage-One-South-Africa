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


def get_excel_spend_money(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_spend_money"]
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
        spendmoney_data = pd.read_excel(path, 'Spend Money')

        grouped_data = spendmoney_data.groupby(["Reference number"])

        job1 = dbname['job'].find({"job_id":job_id})
        job = []
        for i1 in job1:
            job.append(i1) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i2 in coa1:
            coa.append(i2) 
        
        supplier1 = dbname['supplier'].find({"job_id":job_id})
        supplier = []
        for i3 in supplier1:
            supplier.append(i3)

        customer1 = dbname['customer'].find({"job_id":job_id})
        customer = []
        for i4 in customer1:
            customer.append(i4) 
     
        item1 = dbname['item'].find({"job_id":job_id})
        item = []
        for i5 in item1:
            item.append(i5) 
        
        for group_name, df_group in grouped_data:
            QuerySet={'Lines':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            instance_name=None
                
            for row_index, row in df_group.iterrows():
                QuerySet1={}
                date1=str(row['Date']).split(" ")[0]
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")
                
                lineaccountuid={}
                mainaccountuid={}
                category={}

                for j12 in range(0,len(job)):
                    if str(row["Job"]) == job[j12]['Name']:
                        category['UID'] = job[j12]['UID']
                        category['Number'] = job[j12]['Number']
                        category['Name'] = job[j12]['Name']
                        break

                for j1 in range(0,len(coa)):
                    if str(row["Bank Account"]) == coa[j1]['DisplayId']:
                        mainaccountuid["UID"]=coa[j1]["UID"]
                        mainaccountuid["DisplayId"]=coa[j1]["DisplayId"]
                        mainaccountuid["Name"]=coa[j1]["Name"]
                        break
                        
                for j2 in range(0,len(coa)):
                    if str(row["Account"]) == coa[j2]['DisplayId']:
                        lineaccountuid["UID"]=coa[j2]["UID"]
                        lineaccountuid["DisplayId"]=coa[j2]["DisplayId"]
                        lineaccountuid["Name"]=coa[j2]["Name"]
                        break
                        
                supplieruid = {}
                for s1 in range(0, len(supplier)):
                    if row["Contact"] == supplier[s1]['CompanyName']:
                        supplieruid["UID"] = supplier[s1]["UID"]
                
                customeruid={}
                for c1 in range(0,len(customer)):
                    if row["Contact"] == customer[c1]['Company_Name']:
                        customeruid["UID"]=customer[c1]["UID"]
                        customeruid["Type"] = "Customer"
                   
                contactid=None
                if customeruid =={} and supplieruid=={}:
                    contactid=None
                elif customeruid =={} and supplieruid!={}:
                    contactid=supplieruid
                elif customeruid !={} and supplieruid!={}:
                    contactid=customeruid
                    
                QuerySet["PayFrom"]= "Account"
                QuerySet["Account"]= mainaccountuid
                QuerySet1["Job"]= category if category!={} else None
                QuerySet["Contact"]= contactid
                QuerySet["PaymentNumber"]= str(row["Reference number"])
                QuerySet["Date"]= transactiondate1
                QuerySet["AmountPaid"]= round(row["Amount"],2)
                QuerySet["IsTaxInclusive"]= False if row["Amounts are"] == "Tax exclusive" else True
                QuerySet["TotalTax"]= 0
                QuerySet["Memo"]= instance_check(instance_name,row['Description of transaction']) 
                
                tax_code={}
                for i2 in range(0,len(taxJsonResponse1)):
                    if row['Tax Code']==taxJsonResponse1[i2]["Code"]:
                        tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                        break
                    elif row['Tax Code']==taxJsonResponse1[i2]["Description"]:
                        tax_code["UID"]=taxJsonResponse1[i2]["UID"]
                        break
                    else:
                        if taxJsonResponse1[i2]["Code"]=="N-T":
                            tax_code["UID"]=taxJsonResponse1[i2]["UID"]
            
                QuerySet1["Account"]= lineaccountuid
                QuerySet1["TaxCode"]= tax_code
                QuerySet1["Amount"]= round(row["Amount"],2)
                QuerySet1["Memo"]= instance_check(instance_name,row['Description'])
            
                QuerySet['Lines'].append(QuerySet1)
            
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        