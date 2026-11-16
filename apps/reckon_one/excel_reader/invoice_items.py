import traceback
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
import math
from apps.util.qbo_util import instance_check


def get_excel_reckon_invoice_item(job_id,task_id):
    try:
        dbname = get_mongodb_database()

        reckon_item1 = dbname["reckon_item"].find({"job_id":job_id})
        reckon_item = []
        for p1 in reckon_item1:
            reckon_item.append(p1)

        reckon_coa1 = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)

        reckon_invoice1 = dbname["excel_reckon_invoice"].find({"job_id":job_id})
        reckon_invoice = []
        for p1 in reckon_invoice1:
            reckon_invoice.append(p1)
        
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        for i in range(0,len(reckon_invoice)):
            for i1 in range(0,len(reckon_invoice[i]['LineItems'])):
                for j in range(0,len(reckon_item)):
                    if reckon_invoice[i]['LineItems'][i1]['Item'] == reckon_item[j]['FullName']:
                        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)
                        url = f"{base_url}/items?$filter=Id  eq {reckon_item[j]['Id']}"
                        response = requests.request("GET", url, headers=get_headers, data=payload)
                        JsonResponse = response.json()

                        # print("SaleCategoryId",JsonResponse[0]['SaleCategoryId'])


                        for k in range(0,len(reckon_coa)):
                            if reckon_invoice[i]['LineItems'][i1]['Account'] == reckon_coa[k]['AccountCode']:
                                if JsonResponse[0]['SaleCategoryId'] == reckon_coa[k]['Id']:
                                    print("Match")
                                else:
                                    print("Create Item")
                                    
                                
    except Exception as ex:
        traceback.print_exc()


def get_excel_reckon_item(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_item"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        item_data = pd.read_excel(path, 'Item')


        reckon_item1 = dbname["reckon_item"].find({"job_id":job_id})
        reckon_item = []
        for p1 in reckon_item1:
            reckon_item.append(p1)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        instance_name=None
        
        for index, row in item_data.iterrows():

            def get_item_type(value):
                Type=None
                if value == 'Service':
                    Type=2
                elif value == 'Product':
                    Type=1
                return Type
            
            sale_account = None
            for j1 in range(0,len(reckon_item)):
                if str(row['SALE ACCOUNT']) == str(reckon_item[j1]['AccountCode']):
                    sale_account = reckon_item[j1]['Id']
                  
            purchase_account=None 
            for j2 in range(0,len(reckon_item)):
                if str(row['PURCHASE ACCOUNT']) == str(reckon_item[j2]['AccountCode']):
                    purchase_account = reckon_item[j2]['Id']
                    print(purchase_account)
                  

            sale_tax= None
            for j in range(0, len(taxcode_reckon)):
                if row["SALE TAX CODE"] == "GST Free Expenses":
                    if taxcode_reckon[j]['Name'] == 'NCF':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
                elif row["SALE TAX CODE"] == "GST Free Income":
                    if taxcode_reckon[j]['Name'] == 'FRE':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
                elif row["SALE TAX CODE"] == "GST on Expenses":
                    if taxcode_reckon[j]['Name'] == 'NCG':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
                elif row["SALE TAX CODE"] == "GST on Imports":
                    if taxcode_reckon[j]['Name'] == 'INP':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
                elif row["SALE TAX CODE"] == "GST on Income":
                    if taxcode_reckon[j]['Name'] == 'GST':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
                else:
                    if taxcode_reckon[j]['Name'] == 'NTD':
                        sale_tax = taxcode_reckon[j]['ID']
                        break
            

                

            purchase_tax= None
            for j in range(0, len(taxcode_reckon)):
                if row["PURCHASE TAX CODE"] == "GST Free Expenses":
                    if taxcode_reckon[j]['Name'] == 'NCF':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
                elif row["PURCHASE TAX CODE"] == "GST Free Income":
                    if taxcode_reckon[j]['Name'] == 'FRE':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
                elif row["PURCHASE TAX CODE"] == "GST on Expenses":
                    if taxcode_reckon[j]['Name'] == 'NCG':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
                elif row["PURCHASE TAX CODE"] == "GST on Imports":
                    if taxcode_reckon[j]['Name'] == 'INP':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
                elif row["PURCHASE TAX CODE"] == "GST on Income":
                    if taxcode_reckon[j]['Name'] == 'GST':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
                else:
                    if taxcode_reckon[j]['Name'] == 'NTD':
                        purchase_tax = taxcode_reckon[j]['ID']
                        break
            
            
                
            def Sold_Purchased():
                SoldOrPurchased=None
            
                if instance_check(instance_name,row["PURCHASE ACCOUNT"])!=None and instance_check(instance_name,row["SALE ACCOUNT"])!=None:
                    SoldOrPurchased=3
                    
                elif instance_check(instance_name,row["SALE ACCOUNT"])!=None:
                    SoldOrPurchased=1
                    
                elif instance_check(instance_name,row["PURCHASE ACCOUNT"])!=None:
                    SoldOrPurchased=2

                return SoldOrPurchased
            
            item_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "ItemType": get_item_type(row["TYPE"]),
                "Name": str(row["NAME"]).replace(":","-")[0:30],
                "ItemCode": row["CODE"],

                "SaleCategoryId":sale_account,
                "SalePrice":instance_check(instance_name,row["SALE PRICE (GROSS)"]) ,
                "SaleDescription": instance_check(instance_name,row["SALE DESCRIPTION"]),
                "SaleTaxId":sale_tax,

                "PurchaseCategoryId":purchase_account,
                "PurchasePrice":instance_check(instance_name,row["PURCHASE PRICE (GROSS)"]),
                "PurchaseDescription": instance_check(instance_name,row["PURCHASE DESCRIPTION"]),
                "PurchaseTaxId":purchase_tax,
                "ItemStatus":1,

                "IsBought": True if purchase_account else False,
                "IsSold": True if sale_account else False,
                "SoldOrPurchased":Sold_Purchased()
            }
            collection.insert_one(item_payload)

    except Exception as ex:
        traceback.print_exc()


