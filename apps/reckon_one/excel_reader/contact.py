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

def get_reckon_contact(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_contact"]
        no_of_records = db["reckon_contact"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/contacts/15000"
        print(url)

        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 

        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_contact"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["ContactId"] = JsonResponse[i]["ContactId"]
            QuerySet["Description"] = JsonResponse[i]["Description"]
            QuerySet["FirstNameBranchName"] = JsonResponse[i]["FirstNameBranchName"]
            QuerySet["SurnameBusinessName"] = JsonResponse[i]["SurnameBusinessName"]
            QuerySet["IsCustomer"] = JsonResponse[i]["IsCustomer"]
            QuerySet["IsSupplier"] = JsonResponse[i]["IsSupplier"]
            QuerySet["IsEmployee"] = JsonResponse[i]["IsEmployee"]
            QuerySet["IsActive"] = JsonResponse[i]["IsActive"]
            
            arr.append(QuerySet)

        Collection.insert_many(arr)
        print("Added")

    except Exception as ex:
        traceback.print_exc()

