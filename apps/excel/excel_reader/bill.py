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



def get_excel_bill(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_bill"]
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
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        bill_data = pd.read_excel(path, 'Bills')

        grouped_data = bill_data.groupby(["Bill number"])

        job1 = dbname['job'].find({"job_id":job_id})
        job = []
        for i in job1:
            job.append(i) 

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        supplier1 = dbname['supplier'].find({"job_id":job_id})
        supplier = []
        for i in supplier1:
            supplier.append(i) 
 
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
                balanceduedate = datetime.strptime(date2, "%Y-%m-%d")
                balanceduedate1=balanceduedate.strftime("%Y-%m-%d")
                transactiondate = datetime.strptime(date1, "%Y-%m-%d")
                transactiondate1=transactiondate.strftime("%Y-%m-%d")
                duedate = balanceduedate.date().day

                supplieruid = {}
                for j in range(0, len(supplier)):
                    if supplier[j]['CompanyName'] != None:
                        if row["Supplier"] == supplier[j]['CompanyName']:
                            supplieruid["UID"] = supplier[j]["UID"]
                            break
                        elif supplier[j]['CompanyName'].startswith(row["Supplier"]) and supplier[j]['CompanyName'].endswith("- S")  :
                            supplieruid["UID"]=supplier[j]["UID"]
                            break
                        elif row["Supplier"][0:50] == supplier[j]['CompanyName'][0:50]:
                            supplieruid["UID"]=supplier[j]["UID"]
                    
                    elif 'DisplayName' in supplier[j] and supplier[j]['DisplayName'] != None:
                        if row["Supplier"] == supplier[j]['DisplayName']:
                            supplieruid["UID"] = supplier[j]["UID"]
                            break
                        elif supplier[j]['DisplayName'].startswith(row["Supplier"]) and supplier[j]['DisplayName'].endswith("- S")  :
                            supplieruid["UID"]=supplier[j]["UID"]
                            break
                        elif row["Supplier"][0:50] == supplier[j]['DisplayName'][0:50]:
                            supplieruid["UID"]=supplier[j]["UID"]
                    

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
                
                
                QuerySet['Number'] = str(row['Bill number'])[0:13]
                QuerySet["Date"]=transactiondate1
                QuerySet["SupplierInvoiceNumber"]= str(row["Supplier invoice number"])
                QuerySet["Supplier"]= supplieruid
            
                QuerySet["IsTaxInclusive"]= False if row["Amounts are"] == "Tax exclusive" else True
                QuerySet["IsReportable"]= False
                QuerySet['Date'] = transactiondate1
                QuerySet['Total'] = row['Amount ($)']
                # QuerySet["Subtotal"]= row["Unit Price"]*row["No. of Unit"] 
                QuerySet["FreightTaxCode"]= tax_code
                QuerySet["TotalTax"]= 0 if math.isnan(row["Tax amount ($)"]) else float(row['Tax amount ($)'])
                # QuerySet["TotalAmount"]= row["Unit Price"]*row["No. of Unit"]
                terms={}
                terms['PaymentIsDue'] = "DayOfMonthAfterEOM"
                terms['DueDate'] = balanceduedate1
                terms['BalanceDueDate'] = duedate
                terms["Discount"]=0
                QuerySet["Terms"]=terms
                QuerySet1={}
                QuerySet1['Type']='Transaction'
                
                jobuid={}
                for i1 in range(0,len(job)):
                    if job[i1]["Name"]==row['Job name']:
                        jobuid["UID"]=job[i1]["UID"]
                        
                mainaccountuid={}
                for j1 in range(0,len(coa)):
                    if str(row["Account No."]) == coa[j1]['DisplayId']:
                        mainaccountuid["UID"]=coa[j1]["UID"]

                discount = None
                if type(row['Discount %']) == float:
                    
                    if math.isnan(row['Discount %']):
                        discount = 0
                    else:
                        discount = row['Discount %']
                elif type(row['Discount %']) == str:
                    if len(row['Discount %']) == 0:
                        discount = row['Discount %']
                    else:
                        discount = str(row['Discount %'])

                itemuid={}
                for j3 in range(0,len(item)):
                    if row["Item"] == item[j3]['Name']:
                        itemuid["UID"]=item[j3]["UID"]
                QuerySet1['Description'] = instance_check(instance_name,row['Description'])
                
                
                if itemuid != {} and itemuid != None:
                    if row["Unit Price"] >= 0 :
                        QuerySet1["BillQuantity"]= row["No. of Unit"]
                        QuerySet1["UnitCount"]= row["No. of Unit"]
                        QuerySet1["ReceivedQuantity"]= row["No. of Unit"]
                        QuerySet1["BackorderQuantity"]= row["No. of Unit"]
                        QuerySet1["UnitPrice"]= row["Unit Price"]
                        
                    else:
                        QuerySet1["BillQuantity"]= -row["No. of Unit"]
                        QuerySet1["UnitCount"]= -row["No. of Unit"]
                        QuerySet1["BackorderQuantity"]= row["No. of Unit"]
                        QuerySet1["ReceivedQuantity"]= -row["No. of Unit"]
                        QuerySet1["UnitPrice"]= -row["Unit Price"]
                else:
                    if row["Unit Price"] >= 0 :
                        QuerySet1["BillQuantity"]= 0
                        QuerySet1["UnitCount"]= 1
                        QuerySet1["BackorderQuantity"]= 0
                        QuerySet1["ReceivedQuantity"]= 0
                        QuerySet1["UnitPrice"]= row["Unit Price"]
                    else:
                        QuerySet1["BillQuantity"]= 0
                        QuerySet1["UnitCount"]= -1
                        QuerySet1["ReceivedQuantity"]= 0
                        QuerySet1["BackorderQuantity"]= 0
                        QuerySet1["UnitPrice"]= -row["Unit Price"]
                
                QuerySet1['Total'] = round(QuerySet1["BillQuantity"]*QuerySet1["UnitPrice"],2)

                # QuerySet1["Total"]= round(QuerySet1["BillQuantity"]*QuerySet1["UnitPrice"],4)
                    
                QuerySet1["Job"]= jobuid if jobuid != {} else None
                QuerySet1["DiscountPercent"]= discount
                QuerySet1["Account"]= mainaccountuid
                QuerySet1["TaxCode"]= tax_code
                QuerySet1["Item"]= None if itemuid == {} else itemuid  
                QuerySet['Lines'].append(QuerySet1)
            
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        