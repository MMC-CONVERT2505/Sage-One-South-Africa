import traceback
from ast import Break
import os
import requests
import pandas as pd
import openpyxl
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
from datetime import datetime
import math
import collections
from apps.util.qbo_util import instance_check


def get_inactive_suppliers(job_id,task_id):
    try:
        print("get_inactive_suppliers")
        dbname = get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        inactive_supp1 = dbname['excel_reckon_bill'].find({"job_id":job_id})
        inactive_supp = []
        for i in inactive_supp1:
            inactive_supp.append(i)

        update_supp=[]
        for j in range(0,len(inactive_supp)):
            if inactive_supp[j]['SupplierId'] not in update_supp:
                update_supp.append(inactive_supp[j]['SupplierId'])
            else:
                pass
        
        print(update_supp)


        for c1 in range(0,len(update_supp)):
            url = f"{base_url}/contacts/{update_supp[c1]}/activate"
            payload = {}
            files={}
            
            response = requests.request("POST", url, headers=post_headers, data=payload, files=files)
            print(response.text)
            print(response)


    except Exception as ex:
        traceback.print_exc()
    

def get_new_items_from_excel_bill(job_id,task_id):
    try:
        print("get_new_items_from_excel_bill")
        dbname = get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        invoice1 = dbname['excel_reckon_bill'].find({"job_id":job_id})
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
                if 'Item' in invoice_item[j]['LineItems'][j1] and invoice_item[j]['LineItems'][j1]['Item']!=None:
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
                if (unique_items[k]['itemname'] == reckon_item[k1]['FullName']) and (unique_items[k]['accname'] != reckon_item[k1]['PurchaseAccountName']): 
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

                purchase_account=None
                if items_to_be_added[d1]['accname'] == unique_coas[d2]['accname']:
                    purchase_account = unique_coas[d2]['accid']

                item_payload = {
                    "ItemType": 1,
                    "Name": items_to_be_added[d1]['itemname'],
                    "ItemCode": items_to_be_added[d1]['itemname'],
                    "PurchaseCategoryId":purchase_account,
                    "ItemStatus":1,
                    "IsBought": True if purchase_account else False,
                    "IsSold": False,
                    "SoldOrPurchased":2,
                    'IsTaxInclusive':False
                }

                print(item_payload)
                payload = json.dumps(item_payload)
                url = f"{base_url}/items"
                response = requests.request("POST", url, headers=post_headers, data=payload)
                print(response)
      
    except Exception as ex:
        traceback.print_exc()


def get_excel_reckon_bill(job_id,task_id):
    try:
        print("get_excel_reckon_bill")
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_bill"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j in range(0,len(dir)):
            if dir[j].startswith(str(job_id)):
                filename = dir[j]
        
        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        bill_data = pd.read_excel(path, 'Bills')
        grouped_data = bill_data.groupby(["Reference code"])

        tax1 = dbname['taxcode_reckon'].find({"job_id":job_id})
        tax = []
        for i in tax1:
            tax.append(i) 

        coa1 = dbname['reckon_coa'].find({"job_id":job_id})
        coa = []
        for i in coa1:
            coa.append(i) 

        supplier1 = dbname['reckon_contact'].find({"job_id":job_id})
        supplier = []
        for i in supplier1:
            supplier.append(i) 

        
        item1 = dbname['reckon_item'].find({"job_id":job_id})
        item = []
        for i in item1:
            item.append(i) 
        
        term1 = dbname['reckon_term'].find({"job_id":job_id})
        term = []
        for i in term1:
            term.append(i) 

        instance_name=None
        
        for group_index, df_group in grouped_data:
            QuerySet={'LineItems':[]}
            QuerySet['job_id'] = job_id
            QuerySet['task_id'] = task_id
            QuerySet['is_pushed'] = 0
            QuerySet['error'] = None
            QuerySet['payload'] = None
            totaltax=0
            totalamount=0
            for row_index, row in df_group.iterrows():
                
                date1=str(row['Bill date']).split(" ")[0]
                date2=str(row['Due Date']).split(" ")[0]
                
                supplieruid=None
                for j2 in range(0,len(supplier)):
                    if row["Supplier"] == supplier[j2]['Description']:
                        supplieruid=supplier[j2]["ContactId"]
                        break    
                    elif row["Supplier"] == supplier[j2]['FirstNameBranchName']:
                        supplieruid=supplier[j2]["ContactId"]
                        break    
                        
                accountid=None
                if int(row["Account"])==float(row["Account"]):
                    row["Account"]=str(int(row["Account"]))
                    
                for j3 in range(0,len(coa)):
                        
                    if str(row["Account"]) == coa[j3]['AccountCode']:
                        accountid=coa[j3]["Id"]
                        break
                
                itemid=None
                if instance_check(instance_name,row['Item']) !=None:
                    for j5 in range(0,len(item)):
                        if row["Item"] == item[j5]['FullName']:
                            itemid=item[j5]["Id"]
                            continue
                        elif row["Item"].replace(":","-") == item[j5]['FullName']:
                            itemid=item[j5]["Id"]
                            continue
                        elif row["Item"]+"-"+row["Account"] == item[j5]['FullName']:
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
                
                # termid=None
                # for j6 in range(0,len(term)):
                #     if row["Payment terms"] == term[j6]['Name']:
                #         termid=term[j6]["Id"]
                      
                if row['Amounts*'] == 'Non Taxed':
                    AmountTaxStatus=1
                elif row['Amounts*'] == 'Gross (Tax Inclusive)':
                    AmountTaxStatus=2
                elif row['Amounts*'] == 'Net (Tax Exclusive)':
                    AmountTaxStatus=3
                
                totaltax=totaltax+row['Tax Amount']
                totalamount=totalamount+row['Amount']
                
                QuerySet['SupplierId'] = supplieruid
                QuerySet['AmountTaxStatus'] = AmountTaxStatus
                # QuerySet['TermID'] = termid
                QuerySet['BillNumber'] = str(row['Reference code'])
                # QuerySet['BillTax'] = None if instance_check(instance_name,row['Tax Amount'])==0 else instance_check(instance_name,row['Tax Amount'])
                QuerySet['BillTax'] = round(totaltax,4) if totaltax!=0 else 0
                QuerySet['BillAmount'] = round((totalamount + totaltax),4)
                QuerySet['Reference'] = str(row['Reference code'])
                # QuerySet['BillAmount'] = None
                # QuerySet['BIllDiscountAmount'] = None
                # QuerySet['BIllDiscountPercentage'] = None
                # QuerySet['BillTax'] = None
                QuerySet['Notes'] = str(row['NOTES'])
                QuerySet['BillDate'] = date1
                QuerySet['DueDate'] = date2
                
                QuerySet1={}
                QuerySet1['LineNo'] = row_index+1
                QuerySet1['ChargeableItemId']=itemid
                QuerySet1['Item']=instance_check(instance_name,row['Item'])
                QuerySet1['Account']=instance_check(instance_name,row['Account'])
                QuerySet1['DiscountPercent']=instance_check(instance_name,row['Discount'])
                QuerySet1['TaxAmount']=None if instance_check(instance_name,row['Tax Amount'])==0 else instance_check(instance_name,row['Tax Amount'])
                QuerySet1['InvoiceDiscountedTaxAmount']=QuerySet1['TaxAmount']
                    
                amount=round(instance_check(instance_name,row['Qty'])*instance_check(instance_name,row['Item price']),4)
                QuerySet1['Amount']=amount
                QuerySet1['InvoiceDiscountedAmountExTax']=QuerySet1['Amount']
                QuerySet1['AmountExTax']=amount
                QuerySet1['TaxIsModified'] =True
                QuerySet1['IsSubTotal']=False
                QuerySet1['AccountingCategoryId']=accountid
                QuerySet1['AccountId']=accountid if itemid==None else None
                QuerySet1['AccountName']=instance_check(instance_name,row['Account Name'])
                QuerySet1['Description']=instance_check(instance_name,row['Description'])
                QuerySet1['Quantity']=instance_check(instance_name,row['Qty'])
                QuerySet1['UnitPriceExTax']=instance_check(instance_name,row['Item price'])
                QuerySet1['UnitPriceTax']=instance_check(instance_name,row['Tax Amount'])
                QuerySet1['UnitPriceIsTaxInclusive']=False
                QuerySet1['TaxGroupId']=taxgroupid #if QuerySet1['TaxAmount']!=None else None
                
                QuerySet['LineItems'].append(QuerySet1)
                
            collection.insert_one(QuerySet)

    except Exception as ex:
        traceback.print_exc()
        


def get_reckon_bill(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_bill"]
        no_of_records = db["reckon_bill"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/bills/100000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_bill"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["Id"] = JsonResponse[i]["BillID"]
            QuerySet["BillNumber"] = JsonResponse[i]["BillNumber"]
            QuerySet["Balance"] = JsonResponse[i]["Balance"]
            QuerySet["BillAmount"] = JsonResponse[i]["BillAmount"]
            QuerySet["CustomerID"] = JsonResponse[i]["CustomerID"]
            QuerySet["CustomerName"] = JsonResponse[i]["CustomerName"]
            QuerySet["Reference"] = JsonResponse[i]["Reference"]
            QuerySet["IsOverdue"] = JsonResponse[i]['IsOverdue']
            
            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()

