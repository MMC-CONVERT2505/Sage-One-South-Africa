import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database


def get_reckon_taxcode(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["taxcode_reckon"]
        no_of_records = db["taxcode_reckon"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/taxgroups/2000-01-01"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse = response.json()
        JsonResponse = list(JsonResponse)
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "taxcode_reckon"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["ID"] = JsonResponse[i]["ID"]
            QuerySet["Name"] = JsonResponse[i]["Name"]
            QuerySet["Rate"] = JsonResponse[i]["Rate"]
            QuerySet["UseOnPurchases"] = JsonResponse[i]["UseOnPurchases"]
            QuerySet["UseOnSales"] = JsonResponse[i]["UseOnSales"]
            QuerySet["ExportCode"] = JsonResponse[i]["ExportCode"]
            QuerySet["Description"] = JsonResponse[i]["Description"]

            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        
