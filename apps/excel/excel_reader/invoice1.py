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



def get_excel_invoice_new(job_id,task_id):
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
        grouped_data = invoice_data.groupby(["Invoice number"])

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
        instance_name=None
        
        
        for group_name, df_group in grouped_data:
            QuerySet={'Lines':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
                
            for row_index, row in df_group.iterrows():
                date1=str(row['Transaction date']).split(" ")[0]
                date2=str(row['Due date']).split(" ")[0]
                # balanceduedate = datetime.strptime(date2, "%d/%m/%Y")
                # transactiondate = datetime.strptime(date2, "%d/%m/%Y")
                balanceduedate = datetime.strptime(date2, "%Y-%m-%d")
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                balanceduedate1=balanceduedate.strftime("%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")
                duedate = balanceduedate.date().day
               
                QuerySet['CustomerPurchaseOrderNumber'] = row['Customer PO No.']
                QuerySet['Number'] = str(row['Invoice number'])
                QuerySet['Date'] = transactiondate1
                
                QuerySet['IsTaxInclusive'] = False if row["Amounts are"] == 'Tax exclusive' else True
                customeruid={}
                customername = instance_check(instance_name,row['Customer'])
                for j2 in range(0,len(customer)):
                    if customername != None and customer[j2]['Company_Name']!=None:
                        if row["Customer"] == customer[j2]['Company_Name']:
                            customeruid["UID"]=customer[j2]["UID"]
                            break    
                        elif customer[j2]['Company_Name'].startswith(row["Customer"]) and customer[j2]['Company_Name'].endswith("- C")  :
                            customeruid["UID"]=customer[j2]["UID"]
                            break
                        elif customer[j2]['Company_Name'].startswith(row["Customer"]):
                            customeruid["UID"]=customer[j2]["UID"]
                            break
                    
                QuerySet['customer']= None if customeruid=={} else customeruid
                terms={}
                terms['PaymentIsDue'] = 'OnADayOfTheMonth'
                terms['DueDate'] = balanceduedate1
                terms['BalanceDueDate'] = duedate
                QuerySet["Terms"]=terms
                QuerySet1={}
                
                jobuid={}
                for i1 in range(0,len(job)):
                    if job[i1]["Name"]==row['Job name']:
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

                
                itemuid={}
                for j3 in range(0,len(item)):
                    if row["Item"] == item[j3]['Number']:
                        itemuid["UID"]=item[j3]["UID"]
                        break
                    elif row["Item"] == item[j3]['Name']:
                        itemuid["UID"]=item[j3]["UID"]
                        break

                if row['Unit Price']>=0:
                    QuerySet1['ShipQuantity'] = row['No. of Unit']
                    QuerySet1['CostOfGoodsSold'] = row['No. of Unit']
                    QuerySet1['UnitCount'] = row['No. of Unit']
                    QuerySet1['UnitPrice'] = row['Unit Price']
                else:
                    QuerySet1['ShipQuantity'] = -row['No. of Unit']
                    QuerySet1['CostOfGoodsSold'] = -row['No. of Unit']
                    QuerySet1['UnitCount'] = -row['No. of Unit']
                    QuerySet1['UnitPrice'] = abs(row['Unit Price'])
                QuerySet1['Description'] = instance_check(instance_name,row['Description'])
                QuerySet1['DiscountPercent'] = 0 if math.isnan(row["Discount %"]) else float(row["Discount %"])
                QuerySet1['Item'] = None if itemuid=={} else itemuid
                QuerySet1['Account'] = mainaccountuid
                QuerySet1['TaxCode']=tax_code
                QuerySet1['Job']= None if jobuid=={} else jobuid
                QuerySet1['Total']= round(QuerySet1['ShipQuantity']*QuerySet1['UnitPrice'],2)
                QuerySet1['Type'] = "Transaction"
                
                QuerySet['Lines'].append(QuerySet1)
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        