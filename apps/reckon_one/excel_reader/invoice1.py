import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
from flask.helpers import get_root_path
from datetime import datetime
import math
import collections
from apps.util.qbo_util import instance_check
import asyncio
import json
import math


def get_excel_reckon_invoice(job_id,task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_invoice"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        invoice_data = pd.read_excel(path, 'Invoice')
        grouped_data = invoice_data.groupby(["Reference code"])

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

        def round_up(n, decimals=0):
            multiplier = 10 ** decimals
            return math.ceil(n * multiplier) / multiplier
        def round_down(n, decimals=0):
            multiplier = 10 ** decimals
            return math.floor(n * multiplier) / multiplier
        
        
        
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
                dx = instance_check(instance_name,row['Qty'])*instance_check(instance_name,row['Item price'])
                fourth_digit = int((dx * 10000) % 10)
            
                amountextax=0
                if fourth_digit>=5:
                    amountextax=round_up(dx, decimals=4)
                else:
                    amountextax=round_down(dx, decimals=4)


                date1=str(row['Invoice date']).split(" ")[0]
                date2=str(row['Invoice Due date']).split(" ")[0]

                line_no=None
                if row_index == 0:
                    line_no=1
                else:
                    line_no=row_index+1
                
                customeruid=None
                for j2 in range(0,len(customer)):
                    if row["Customer"].lower().strip() == customer[j2]['Description'].lower().strip():
                        customeruid=customer[j2]["ContactId"]
                        break    
                    elif row["Customer"].lower().strip() == customer[j2]['FirstNameBranchName'].lower().strip():
                        customeruid=customer[j2]["ContactId"]
                        break    
                        
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
                    if str(row["Item"]) == item[j5]['FullName']:
                        itemid=item[j5]["Id"]
                        continue
                    elif str(row["Item"]).replace(":","-") == item[j5]['FullName']:
                        itemid=item[j5]["Id"]
                        continue
                    elif str(row["Item"])+"-"+str(row['Account']) == item[j5]['FullName']:
                        itemid=item[j5]["Id"]
                        break
                   
                taxgroupid=None
                for j4 in range(0,len(tax)):
                    if row["Tax code"] == tax[j4]['Name']:
                        taxgroupid=tax[j4]["ID"]
                        break
                    elif row["Tax code"] == tax[j4]['Description']:
                        taxgroupid=tax[j4]["ID"]
                        break


                termid=None
                for j6 in range(0,len(term)):
                    if row["Payment terms"] == term[j6]['Name']:
                        termid=term[j6]["Id"]

                AmountTaxStatus=1  
                if row['Amounts*'] == 'Non Taxed':
                    AmountTaxStatus=1
                elif row['Amounts*'] == 'Net (Tax Inclusive)':
                    AmountTaxStatus=2
                elif row['Amounts*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3

                # tax_data=row['Tax Amount']/row['Qty']
                
                totaltax=totaltax+row['Tax Amount']
                totalamount=totalamount+row['Amount']
                
                if AmountTaxStatus ==1 or AmountTaxStatus==3:
                    QuerySet['CustomerId'] = customeruid
                    QuerySet['AmountTaxStatus'] = AmountTaxStatus
                    QuerySet['TermID'] = termid
                    QuerySet['InvoiceNumber'] = str(instance_check(instance_name,row['Reference code'])) if instance_check(instance_name,row['Reference code'])!=None else None
                    QuerySet['InvoiceTax'] = round(totaltax,4) if totaltax!=0 else 0
                    QuerySet['InvoiceAmount'] = round((totalamount + totaltax),4)
                    QuerySet['Reference'] = str(instance_check(instance_name,row['Reference code'])) if instance_check(instance_name,row['Reference code'])!=None else None
                    QuerySet['PaymentDetails'] = instance_check(instance_name,row['PAYMENT DETAILS']) 
                    # QuerySet['InvoiceDiscountAmount'] = 0
                    # QuerySet['InvoiceDiscountPercentage'] = 0
                    QuerySet['Notes'] = instance_check(instance_name,row['NOTE'])
                    QuerySet['InvoiceDate'] = date1
                    QuerySet['DueDate'] = date2
                    
                    QuerySet1={}
                    QuerySet1['Item']=row['Item']
                    QuerySet1['ChargeableItemId']=itemid if itemid!=None else None
                    QuerySet1['Account']=row['Account']
                    QuerySet1['AccountName']=row['Account Name']
                    # QuerySet1['DiscountPercent']=0 if instance_check(instance_name,row['Discount'])==None else instance_check(instance_name,row['Discount'])
                    QuerySet1['TaxAmount']=0 if instance_check(instance_name,row['Tax Amount'])==0 else round(instance_check(instance_name,row['Tax Amount']),4)
                    # QuerySet1['InvoiceDiscountedTaxAmount']=QuerySet1['TaxAmount']
                    QuerySet1['Amount']=round(row['Amount'],4)
                    # QuerySet1['AmountExTax']=round(instance_check(instance_name,row['Qty'])*instance_check(instance_name,row['Item price']),4)
                    QuerySet1['AmountExTax']=amountextax
                    # QuerySet1['InvoiceDiscountedAmountExTax']=QuerySet1['Amount']
                    QuerySet1['IsSubTotal']=False
                    QuerySet1['AccountId']=accountid if itemid==None else None
                    QuerySet1['Description']=instance_check(instance_name,row['Description'])
                    QuerySet1['Quantity']=instance_check(instance_name,row['Qty'])
                    QuerySet1['UnitPriceExTax']=round(instance_check(instance_name,row['Item price']),10)
                    QuerySet1['UnitPriceTax']=0
                    QuerySet1['TaxIsModified']=True
                    QuerySet1['UnitPriceIsTaxInclusive']=False
                    QuerySet1['TaxGroupId']=taxgroupid #if QuerySet1['TaxAmount']!=0 else None
                    QuerySet['LineItems'].append(QuerySet1)
                else:
                    QuerySet['CustomerId'] = customeruid
                    QuerySet['AmountTaxStatus'] = AmountTaxStatus
                    QuerySet['TermID'] = termid
                    QuerySet['InvoiceNumber'] = str(row['Reference code'])
                    QuerySet['InvoiceTax'] = round(totaltax,4) if totaltax!=0 else 0
                    QuerySet['InvoiceAmount'] = round((totalamount),4)
                    QuerySet['Reference'] = str(row['Reference code'])
                    QuerySet['PaymentDetails'] = str(row['PAYMENT DETAILS'])
                    # QuerySet['InvoiceDiscountAmount'] = 0
                    # QuerySet['InvoiceDiscountPercentage'] = 0
                    QuerySet['Notes'] = str(row['NOTE'])
                    QuerySet['InvoiceDate'] = date1
                    QuerySet['DueDate'] = date2
                    
                    QuerySet1={}
                    QuerySet1['TaxIsModified']=True

                    QuerySet1['Account']=row['Account']
                    QuerySet1['Item']=row['Item']
                    QuerySet1['ChargeableItemId']=itemid
                    QuerySet1['AccountName']=row['Account Name']
                   
                    # QuerySet1['DiscountPercent']=instance_check(instance_name,row['Discount'])
                    QuerySet1['TaxAmount']=0 if instance_check(instance_name,row['Tax Amount'])==0 else round(instance_check(instance_name,row['Tax Amount']),4)
                    # QuerySet1['InvoiceDiscountedTaxAmount']=QuerySet1['TaxAmount']
                    QuerySet1['Amount']=round(row['Amount'],4)
                    QuerySet1['AmountExTax']=round(QuerySet1['Amount']-QuerySet1['TaxAmount'],4)
                    # QuerySet1['InvoiceDiscountedAmountExTax']=QuerySet1['Amount']-QuerySet1['TaxAmount']
                    QuerySet1['IsSubTotal']=False
                    QuerySet1['AccountId']=accountid if itemid==None else None
                    QuerySet1['Description']=instance_check(instance_name,row['Description'])
                    QuerySet1['Quantity']=instance_check(instance_name,row['Qty'])
                    QuerySet1['UnitPriceExTax']=round((QuerySet1['Amount']-QuerySet1['TaxAmount'])/row['Qty'],10)
                    # QuerySet1['UnitPriceExTax'] = ((row['Qty']*row['Item price']) - (row['Qty']*row['Item price']*row['Discount']/100))/row['Qty']
                    QuerySet1['UnitPriceTax']=round(QuerySet1['TaxAmount']/row['Qty'],10)
                    QuerySet1['UnitPriceIsTaxInclusive']=False
                    QuerySet1['TaxGroupId']=taxgroupid
                    QuerySet['LineItems'].append(QuerySet1)
                    
                    
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()


def get_inactive_customers(job_id,task_id):
    try:
        print("get_inactive_customers")
        dbname = get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        inactive_cust1 = dbname['excel_reckon_invoice'].find({"job_id":job_id})
        inactive_cust = []
        for i in inactive_cust1:
            inactive_cust.append(i)

        update_cust=[]
        for j in range(0,len(inactive_cust)):
            if inactive_cust[j]['CustomerId'] not in update_cust:
                update_cust.append(inactive_cust[j]['CustomerId'])
            else:
                pass

        print(update_cust)


        for c1 in range(0,len(update_cust)):
            url = f"{base_url}/contacts/{update_cust[c1]}/activate"
            payload = {}
            files={}
            
            response = requests.request("POST", url, headers=post_headers, data=payload, files=files)
            print(response.text)
            print(response)


    except Exception as ex:
        traceback.print_exc()
    

def get_new_items_from_excel_invoice(job_id,task_id):
    try:
        print("get_new_items_from_excel")
        dbname = get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        invoice1 = dbname['excel_reckon_invoice'].find({"job_id":job_id})
        invoice_item = []
        for i in invoice1:
            invoice_item.append(i)

        coa1 = dbname['reckon_coa'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i)

        reckon_item1 = dbname['reckon_item'].find({"job_id":job_id})
        reckon_item = []
        for i in reckon_item1:
            reckon_item.append(i)

        new_item=[]
        for j in range(0,len(invoice_item)):
            for j1 in range(0,len(invoice_item[j]['LineItems'])):
                e={}
                e['itemname'] = invoice_item[j]['LineItems'][j1]['Item']
                e['accname'] = invoice_item[j]['LineItems'][j1]['AccountName']
                e['acccode'] = invoice_item[j]['LineItems'][j1]['Account']
                
                new_item.append(e)

        unique_items = []
        seen_items = set()

        for item in new_item:
            item_tuple = (item['itemname'], item['accname'])
            if item_tuple not in seen_items:
                seen_items.add(item_tuple)
                unique_items.append(item)
       
        items_to_be_added=[]
            
        for k1 in range(0,len(reckon_item)):
            for k in range(0,len(unique_items)):
                e1={}
                if (unique_items[k]['itemname'] == reckon_item[k1]['FullName']) and (unique_items[k]['accname'] != reckon_item[k1]['SaleAccountName']): 
                    e1['itemname'] = unique_items[k]['itemname']+"-"+unique_items[k]['acccode']
                    e1['accname'] = unique_items[k]['accname']
                    items_to_be_added.append(e1)
                    
        req_coa=[]
        for c1 in range(0,len(coa)):
            for k2 in range(0,len(unique_items)):
                e2={}
                if (unique_items[k2]['accname'] == coa[c1]['Name']): 
                    e2['accname'] = coa[c1]['Name']
                    e2['accid'] = coa[c1]['Id']
                    e2['acccode'] = coa[c1]['AccountCode']
                    req_coa.append(e2)

        unique_coas = []
        seen_coas = set()

        for coa in req_coa:
            coa_tuple = (coa['accname'], coa['accid'], coa['acccode'])
            if coa_tuple not in seen_coas:
                seen_coas.add(coa_tuple)
                unique_coas.append(coa)

        print(items_to_be_added,"items_to_be_added---")
        print(unique_coas,"req_coa----------------------")

        for d1 in range(0,len(items_to_be_added)):
            for d2 in range(0,len(unique_coas)):

                sale_account=None
                if items_to_be_added[d1]['accname'] == unique_coas[d2]['accname']:
                    sale_account = unique_coas[d2]['accid']

                item_payload = {
                    "ItemType": 1,
                    "Name": items_to_be_added[d1]['itemname'],
                    "ItemCode": items_to_be_added[d1]['itemname'],
                    "SaleCategoryId":sale_account,
                    "SalePrice":0,
                    "SaleDescription": None,
                    "ItemStatus":1,
                    "IsBought": False,
                    "IsSold": True if sale_account else False,
                    "SoldOrPurchased":1,
                    'IsTaxInclusive':False
                }

                print(item_payload)
                payload = json.dumps(item_payload)
                url = f"{base_url}/items"
                response = requests.request("POST", url, headers=post_headers, data=payload)
                print(response)
      
    except Exception as ex:
        traceback.print_exc()


def get_reckon_invoice(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_invoice"]
        no_of_records = db["reckon_invoice"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/invoices/10000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_invoice"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["Id"] = JsonResponse[i]["Id"]
            QuerySet["InvoiceNumber"] = JsonResponse[i]["InvoiceNumber"]
            QuerySet["Balance"] = JsonResponse[i]["Balance"]
            QuerySet["CustomerID"] = JsonResponse[i]["CustomerID"]
            QuerySet["CustomerName"] = JsonResponse[i]["CustomerName"]
            QuerySet["InvoiceAmount"] = JsonResponse[i]["InvoiceAmount"]
            QuerySet["Reference"] = JsonResponse[i]["Reference"]
            QuerySet["IsOverdue"] = JsonResponse[i]['IsOverdue']
            
            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()

