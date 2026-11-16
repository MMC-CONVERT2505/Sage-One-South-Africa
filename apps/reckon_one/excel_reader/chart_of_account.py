import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
import os
from apps.util.qbo_util import instance_check

import pandas as pd
import openpyxl

def get_reckon_chart_of_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_coa"]
        no_of_records = db["reckon_coa"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/accounts/1000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_coa"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["Id"] = JsonResponse[i]["Id"]
            QuerySet["Name"] = JsonResponse[i]["Name"]
            QuerySet["AccountType"] = JsonResponse[i]["AccountType"]
            QuerySet["ParentAccountingCategoryId"] = JsonResponse[i]["ParentAccountingCategoryId"]
            QuerySet["ExportCode"] = JsonResponse[i]["ExportCode"]
            QuerySet["AccountCode"] = JsonResponse[i]["AccountCode"]
            QuerySet["Description"] = JsonResponse[i]["Description"]
            QuerySet["DefaultTaxCode"] = JsonResponse[i]["DefaultTaxCode"]

            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()


def get_reckon_chart_of_account_excel(job_id, task_id):
    print("coa data function")
    try:
        db = get_mongodb_database()
        collection = db["reckon_coa"]
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/accounts/1000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1.get("Items", [])

        print(JsonResponse1,"JsonResponse1---------")

        arr = []
        for item in JsonResponse:
            record = {
                "job_id": job_id,
                "task_id": task_id,
                "table_name": "reckon_coa",
                "error": None,
                "is_pushed": 0,
                "Id": item.get("Id"),
                "Name": item.get("Name"),
                "AccountType": item.get("AccountType"),
                "ParentAccountingCategoryId": item.get("ParentAccountingCategoryId"),
                "ExportCode": item.get("ExportCode"),
                "AccountCode": item.get("AccountCode"),
                "Description": item.get("Description"),
                "DefaultTaxCode": item.get("DefaultTaxCode")
            }
            arr.append(record)

        if arr:
            collection.insert_many(arr)

            print(arr,"arrr data ")
           
            # Export to Excel
            df = pd.DataFrame(arr)
            os.makedirs("output", exist_ok=True)
            excel_file_path = os.path.join("output", f"reckon_coa_{job_id}.xlsx")
            df.to_excel(excel_file_path, index=False)
           
    except Exception as ex:
        traceback.print_exc()
       


def get_reckon_bank_account(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_bank_account"]
        no_of_records = db["reckon_bank_account"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/bankaccounts/1000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_bankaccount"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["BankAccountID"] = JsonResponse[i]["BankAccountID"]
            QuerySet["BankName"] = JsonResponse[i]["Description"]
            # QuerySet["IsBankAccountedOpened"] = JsonResponse[i]["IsBankAccountedOpened"]
            # QuerySet["IsCash"] = JsonResponse[i]["IsCash"]
            
            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()


def get_excel_reckon_chart_of_account(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_chart_of_account"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        coa_data = pd.read_excel(path, 'Account')

        reckon_coa1 = dbname["reckon_coa"].find({"job_id":job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id":job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        for index, row in coa_data.iterrows():
            TaxGroupId = None
            for j in range(0, len(taxcode_reckon)):
                if row["DEFAULT TAX CODE"] == taxcode_reckon[j]['Name']:
                    TaxGroupId = taxcode_reckon[j]['ID']
                    break
                elif taxcode_reckon[j]['Name'] == 'NTD':
                    TaxGroupId = taxcode_reckon[j]['ID']
                    break
            
            sub_account = None
            for k in range(0, len(reckon_coa)):
                if instance_check(sub_account,row["Sub-account"]) == reckon_coa[k]['Name']:
                    sub_account = reckon_coa[k]['Id']
                    break

             
            def get_account_type(value):
                account_type=None
                if value in ['Income','income']:
                    account_type=1
                elif value == 'Expense':
                    account_type=2
                elif value in ['Current asset','Other Current Asset']:
                    account_type=3
                elif value in ['Other current liability','Non-current liability','Other Current Liability']:
                    account_type=4
                elif value == 'Equity':
                    account_type=5
                elif value in ['Other Income','Other income']:
                    account_type=6
                elif value in ['Other Expense','Other expense']:
                    account_type=7
                elif value == 'Cost of goods sold':
                    account_type=8
                elif value == 'Fixed asset':
                    account_type=11
                elif value == 'Other noncurrent asset':
                    account_type=12
                elif value == 'Non current liability':
                    account_type=16
                elif value == 'Bank':
                    account_type=1
                elif value == 'Credit Card':
                    account_type=14
                    
                return account_type
                
            BulkElectronicPaymentSettings={}
            
            
            # EFT['EFT2'] = str(row["ACCOUNT CODE"])
            acccode=None
            if instance_check(sub_account,row["ACCOUNT CODE"])!=None:
                if type(instance_check(sub_account,row["ACCOUNT CODE"])) == float:
                    if instance_check(sub_account,row["ACCOUNT CODE"]) == int(instance_check(sub_account,row["ACCOUNT CODE"])):
                        acccode=int(instance_check(sub_account,row["ACCOUNT CODE"]))
                    else:
                        acccode=instance_check(sub_account,row["ACCOUNT CODE"])
                elif type(instance_check(sub_account,row["ACCOUNT CODE"])) == int:
                    acccode=int(instance_check(sub_account,row["ACCOUNT CODE"]))
            

            EFT={}
            EFT['AccountName'] = row["ACCOUNT NAME"].replace(":","-")[0:15] if instance_check(sub_account,row["ACCOUNT NAME"])!=None else None
            EFT['EFT1'] = int(acccode) if instance_check(sub_account,row["BSB"])==None else instance_check(sub_account,row["BSB"])
            EFT['EFT2'] = int(acccode) if instance_check(sub_account,row["BSB"])==None else instance_check(sub_account,row["BSB"])
            BulkElectronicPaymentSettings['AccountName'] = EFT['AccountName']
            
            coa_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "payload": "",
                "error": "",
                "AccountName": instance_check(sub_account,row["ACCOUNT NAME"]).replace(":","-") if instance_check(sub_account,row["ACCOUNT NAME"])!=None else None,
                "TYPE": row["TYPE"],
                "AccountType": get_account_type(row['TYPE']),
                "Status":int(row['Status']),
                "AccountCode": acccode,
                "ParentAccountingCategoryId": sub_account if sub_account!=None else "00000000-0000-0000-0000-000000000000",
                "Hint": instance_check(sub_account,row["DESCRIPTION"]),
                # "TaxGroupId": TaxGroupId,
                "BankAccountStatus" : 1 if row['Status']==1 else 0,
                "BulkElectronicPaymentSettings" : BulkElectronicPaymentSettings,
                "EFT" :EFT,
                "Description": instance_check(sub_account,row["ACCOUNT NAME"]).replace(":","-") if instance_check(sub_account,row["ACCOUNT NAME"])!=None else None
                
                }

            collection.insert_one(coa_payload)

    except Exception as ex:
        traceback.print_exc()
