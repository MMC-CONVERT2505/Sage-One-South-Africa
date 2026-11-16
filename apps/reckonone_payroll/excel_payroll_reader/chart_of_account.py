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
from apps.util.log_file import log_config

def get_reckon_chart_of_account(job_id,task_id):
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_reckon_chart_of_account")
        db = get_mongodb_database()
        Collection = db["reckon_coa"]
        no_of_records = db["reckon_coa"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/accounts/1000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_reckon_chart_of_account--> url -->{url} response status -->{response.status_code}")
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
        logging.info(f"{job_id} inserted many data in reckon_coa")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)


def get_reckon_bank_account(job_id,task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_reckon_bank_account")
        db = get_mongodb_database()
        Collection = db["reckon_bank_account"]
        no_of_records = db["reckon_bank_account"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/bankaccounts/1000"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_reckon_bank_account--> url-->{url} response status-->{response.status_code}")
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
        logging.info(f"{job_id} inserted many data in reckon_bank_account")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)


