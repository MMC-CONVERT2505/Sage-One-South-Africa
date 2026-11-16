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



def get_excel_reckon_creditnote(job_id,task_id):
    try:
        print("get_excel_reckon_creditnote")
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_creditnote"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        invoice_data = pd.read_excel(path, 'Credit Memo')
        grouped_data = invoice_data.groupby(["Credit Memo"])

        tax1 = dbname['taxcode_reckon'].find({"job_id":job_id})
        tax = []
        for i in tax1:
            tax.append(i) 

        coa1 = dbname['reckon_coa'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        customer1 = dbname['reckon_contact'].find({"job_id":job_id})
        customer = []
        for i in customer1:
            customer.append(i) 

        
        item1 = dbname['reckon_item'].find({"job_id":job_id})
        item = []
        for i in item1:
            item.append(i) 
        
        term1 = dbname['reckon_term'].find({"job_id":job_id})
        term = []
        for i in term1:
            term.append(i) 

        instance_name=None
        
        
        for group_name, df_group in grouped_data:
            QuerySet={'LineItems':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            totaltax=0
            totalamount=0
            for row_index, row in df_group.iterrows():
                date1=str(row['Adjustment note date']).split(" ")[0]
             
                line_no=None
                if row_index == 0:
                    line_no=1
                else:
                    line_no=row_index+1
                
                customeruid=None
                for j2 in range(0,len(customer)):
                    if row["Customer"] == customer[j2]['Description']:
                        customeruid=customer[j2]["ContactId"]
                        break    
                    elif row["Customer"] == customer[j2]['FirstNameBranchName']:
                        customeruid=customer[j2]["ContactId"]
                        break  
                    else:
                        print(row["Customer"])  
                        
                accountid=None
                if int(row["Account"])==float(row["Account"]):
                    row["Account"]=str(int(row["Account"]))
                    
                for j3 in range(0,len(coa)):
                    if 'AccountCode' in coa[j3]:
                        if str(row["Account"]) == coa[j3]['AccountCode']:
                            accountid=coa[j3]["Id"]
                            break
                    else:
                        continue
                
                itemid=None
                for j5 in range(0,len(item)):
                    if row["Item"] == item[j5]['FullName']:
                        itemid=item[j5]["Id"]
                        break
                    elif str(row["Item"]).replace(":","-") == item[j5]['FullName']:
                        itemid=item[j5]["Id"]
                        break
                
                taxgroupid=None
                for j4 in range(0,len(tax)):
                    if row["Tax code"] == tax[j4]['Name']:
                        taxgroupid=tax[j4]["ID"]

                termid=None
                # for j6 in range(0,len(term)):
                #     if row["Payment terms"] == term[j6]['Name']:
                #         termid=term[j6]["Id"]

                AmountTaxStatus=1  
                if row['Amounts*'] == 'Non Taxed':
                    AmountTaxStatus=1
                elif row['Amounts*'] in ['Net (Tax Inclusive)','Gross (Tax Inclusive)']:
                    AmountTaxStatus=2
                elif row['Amounts*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3

                totaltax=totaltax+row['Tax Amount']
                totalamount=totalamount+row['Amount']

                QuerySet['CustomerId'] = customeruid
                QuerySet['TermID'] = termid
                QuerySet['CreditNoteNumber'] = str(row['Credit Memo'])
                QuerySet['Tax'] = round(totaltax,4) if totaltax!=0 else 0
                QuerySet['Amount'] = round((totalamount + totaltax),4)
                QuerySet['Reference'] = str(instance_check(instance_name,row['Credit Memo'])) if instance_check(instance_name,row['Credit Memo'])!=None else None
                QuerySet['InvoiceDiscountAmount'] = None
                QuerySet['InvoiceDiscountPercentage'] = None
                QuerySet['Notes'] = instance_check(instance_name,row['NOTE'])
                QuerySet['CreditNoteDate'] = date1
                
                QuerySet1={}
                QuerySet1['Item']=row['Item']
                QuerySet1['LineNo'] = line_no
                
                QuerySet1['ChargeableItemId']=itemid
                QuerySet1['Account']=row['Account']
                # QuerySet1['DiscountPercent']=instance_check(instance_name,row['Discount'])
                QuerySet1['TaxAmount']=None if instance_check(instance_name,row['Tax Amount'])==0 else round(instance_check(instance_name,row['Tax Amount']),4)
                QuerySet1['InvoiceDiscountedTaxAmount']=QuerySet1['TaxAmount']
                QuerySet1['Amount']=round(row['Amount'],4)
                QuerySet1['AmountExTax']=round(instance_check(instance_name,row['Qty'])*instance_check(instance_name,row['Item price']),4)
                QuerySet1['InvoiceDiscountedAmountExTax']=QuerySet1['Amount']
                QuerySet1['IsSubTotal']=False
                QuerySet1['AccountId']=accountid if itemid==None else None
                QuerySet1['Description']=instance_check(instance_name,row['Description'])
                QuerySet1['Quantity']=instance_check(instance_name,row['Qty'])
                QuerySet1['UnitPriceExTax']=round(instance_check(instance_name,row['Item price']),10)
                QuerySet1['UnitPriceTax']=0
                QuerySet1['UnitPriceIsTaxInclusive']=False
                QuerySet1['TaxGroupId']=taxgroupid if QuerySet1['TaxAmount']!=None else None
                QuerySet['AmountTaxStatus'] = AmountTaxStatus

                QuerySet['LineItems'].append(QuerySet1)

                    
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()



# def get_reckon_creditnote(job_id,task_id):
#     try:
#         db = get_mongodb_database()
#         Collection = db["reckon_creditnote"]
#         no_of_records = db["reckon_creditnote"].count_documents({"job_id":job_id})
#         payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

#         url = f"{base_url}/invoices/1000"
#         response = requests.request("GET", url, headers=get_headers, data=payload)
#         JsonResponse1 = response.json()
#         JsonResponse = JsonResponse1['Items'] 
        
#         arr = []
#         for i in range(0, len(JsonResponse)):
#             QuerySet = {}
#             QuerySet["job_id"] = job_id
#             QuerySet["task_id"] = task_id
#             QuerySet['table_name'] = "reckon_creditnote"
#             QuerySet['error'] = None
#             QuerySet["is_pushed"] = 0
#             QuerySet["Id"] = JsonResponse[i]["Id"]
#             QuerySet["CreditNoteNumber"] = JsonResponse[i]["CreditNoteNumber"]
#             QuerySet["Balance"] = JsonResponse[i]["Balance"]
#             QuerySet["CustomerID"] = JsonResponse[i]["CustomerID"]
#             QuerySet["CustomerName"] = JsonResponse[i]["CustomerName"]
#             QuerySet["CreditNoteAmount"] = JsonResponse[i]["CreditNoteAmount"]
#             QuerySet["Reference"] = JsonResponse[i]["Reference"]
#             QuerySet["IsOverdue"] = JsonResponse[i]['IsOverdue']
            
#             arr.append(QuerySet)

#         Collection.insert_many(arr)

#     except Exception as ex:
#         traceback.print_exc()

