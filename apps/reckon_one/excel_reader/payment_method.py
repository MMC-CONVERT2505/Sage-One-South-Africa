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


def get_reckon_payment_method(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_payment_method"]
        no_of_records = db["reckon_payment_method"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = "https://api.reckon.com/r1//PaymentMethods/AU"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse = response.json()
        # JsonResponse = JsonResponse1['Items']
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_payment_method"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["Id"] = JsonResponse[i]["Id"]
            QuerySet["Description"] = JsonResponse[i]["Description"]
            
            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()

