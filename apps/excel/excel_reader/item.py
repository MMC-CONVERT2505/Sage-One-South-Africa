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


def get_excel_item(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_item"]
        payload, base_url, headers = get_settings_myob(job_id)
        tax_url = f"{base_url}/GeneralLedger/TaxCode"
        account_url = f"{base_url}/GeneralLedger/Account"

        taxresponse = requests.request("GET", tax_url, headers=headers, data=payload)
        taxJsonResponse = taxresponse.json()
        taxJsonResponse1 = taxJsonResponse["Items"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j3 in range(len(dir)):
            if dir[j3].startswith(str(job_id)):
                filename = dir[j3]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        item_data = pd.read_excel(path, 'Item')

        coa1 = dbname['chart_of_account'].find({"job_id": job_id})
        coa = list(coa1)
        supplier1 = dbname['supplier'].find({"job_id": job_id})
        supplier = list(supplier1)

        instance_name=None
        for index, row in item_data.iterrows():
            tax_code = {}
            for i in range(len(taxJsonResponse1)):
                if taxJsonResponse1[i]["Code"] == row['Tax code']:
                    tax_code["UID"] = taxJsonResponse1[i]["UID"]
                    break
                elif taxJsonResponse1[i]["Code"] == "N-T":
                    tax_code["UID"] = taxJsonResponse1[i]["UID"]
                    break

            expenseaccountuid = {}
            incomeaccountuid = {}
            
            for j in range(len(coa)):
                if str(row["Expense account for tracking purchases"]) == coa[j]['DisplayId']:
                    expenseaccountuid["UID"] = coa[j]["UID"]
                    expenseaccountuid["DisplayId"] = coa[j]["DisplayId"]
                    expenseaccountuid["Name"] = coa[j]["Name"]
                    break

            for j2 in range(len(coa)):
                if str(row["Income account for tracking sales"]) == coa[j2]['DisplayId']:
                    incomeaccountuid["UID"] = coa[j2]["UID"]
                    incomeaccountuid["DisplayId"] = coa[j2]["DisplayId"]
                    incomeaccountuid["Name"] = coa[j2]["Name"]
                    break

            RestockingInformation={}
            supp={}

            for s1 in range(len(supplier)):
                if row['Primary supplier for reorders'] == supplier[s1]['CompanyName']:
                    supp['UID'] = supplier[s1]['UID']
                    supp['Name'] = supplier[s1]['CompanyName']

            RestockingInformation['DefaultOrderQuantity'] = 0 if instance_check(instance_name,row['Default reorder quantity (per buying unit)'])==None else instance_check(instance_name,row['Default reorder quantity (per buying unit)'])
            RestockingInformation['Supplier'] = supp

            item_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "Number": row["Item ID"],
                "Name": str(row["Name"])[0:30],
                "Description": row["Description"],
                "UseDescription": True,
                "IsBought": True if expenseaccountuid else False,
                "IsSold": True if incomeaccountuid else False,
                "IsInventoried": False,
                "ExpenseAccount": expenseaccountuid if expenseaccountuid else None,
                "IncomeAccount": incomeaccountuid if incomeaccountuid else None,
                "SellingDetails": {
                    "BaseSellingPrice": 0 if math.isnan(row["Selling Price"]) else row["Selling Price"],
                    "TaxCode": tax_code,
                    "IsTaxInclusive": False
                },
                
                "BuyingDetails": 
                {
                    "StandardCost": 0 if math.isnan(row["Buying price"]) else row["Buying price"],
                    "TaxCode": tax_code,
                    # "StandardCostTaxInclusive": False,
                    "RestockingInformation":RestockingInformation if supp!={} else None
                } if expenseaccountuid else None
            }

            collection.insert_one(item_payload)

    except Exception as ex:
        traceback.print_exc()


def get_excel_item_to_update(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_item_new"]
        payload, base_url, headers = get_settings_myob(job_id)
        tax_url = f"{base_url}/GeneralLedger/TaxCode"
        account_url = f"{base_url}/GeneralLedger/Account"

        taxresponse = requests.request("GET", tax_url, headers=headers, data=payload)
        taxJsonResponse = taxresponse.json()
        taxJsonResponse1 = taxJsonResponse["Items"]

        dir = os.listdir(os.path.join(get_root_path('apps'), 'files/'))
        for j3 in range(len(dir)):
            if dir[j3].startswith(str(job_id)):
                filename = dir[j3]

        path = os.path.join(get_root_path('apps'), 'files/', filename)
        data1 = openpyxl.load_workbook(path)
        sheets = data1.sheetnames
        item_data = pd.read_excel(path, 'Item')

        coa1 = dbname['chart_of_account'].find({"job_id": job_id})
        coa = list(coa1)
        item1 = dbname['item'].find({"job_id": job_id})
        item = list(item1)

        for index, row in item_data.iterrows():
            tax_code = {}
            for i in range(len(taxJsonResponse1)):
                if taxJsonResponse1[i]["Code"] == row['Tax code']:
                    tax_code["UID"] = taxJsonResponse1[i]["UID"]
                    break
                elif taxJsonResponse1[i]["Code"] == "N-T":
                    tax_code["UID"] = taxJsonResponse1[i]["UID"]
                    break

            expenseaccountuid = {}
            incomeaccountuid = {}
            
            rowversion = 0
            t1=dbname["item"].find({"Number": str(row["Item number"]),'job_id':job_id})
            for x in t1:
                rowversion = x.get("RowVersion")

            t2=dbname["chart_of_account"].find({"DisplayId": str(row["Income account for tracking sales"]),'job_id':job_id})
            for x1 in t2:
                incomeaccountuid["UID"] = x1.get("UID")
                incomeaccountuid["DisplayId"] = x1.get("DisplayId")
                incomeaccountuid["Name"] = x1.get("Name")

            t3=dbname["chart_of_account"].find({"DisplayId": str(row["Expense account for tracking purchases"]),'job_id':job_id})
            for x3 in t3:
                expenseaccountuid["UID"] = x3.get("UID")
                expenseaccountuid["DisplayId"] = x3.get("DisplayId")
                expenseaccountuid["Name"] = x3.get("Name")
                
            item_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "UID": row["UID"],
                "Name": str(row["NewNme"])[0:30],
                "Number": str(row["Item ID"]),
                "RowVersion": rowversion,
                "Description": row["Description"],
                "UseDescription": True,
                "IsBought": True if expenseaccountuid else False,
                "IsSold": True if incomeaccountuid else False,
                "IsInventoried": False,
                "ExpenseAccount": expenseaccountuid if expenseaccountuid else None,
                "IncomeAccount": incomeaccountuid if incomeaccountuid else None,
                "SellingDetails": {
                    "BaseSellingPrice": 0 if math.isnan(row["Selling Price"]) else row["Selling Price"],
                    "TaxCode": tax_code,
                    "IsTaxInclusive": False
                },
                "BuyingDetails": {
                    "StandardCost": 0 if math.isnan(row["Buying price"]) else row["Buying price"],
                    "TaxCode": tax_code,
                    "StandardCostTaxInclusive": False
                }
            }


            collection.insert_one(item_payload)

    except Exception as ex:
        traceback.print_exc()


