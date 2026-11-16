import traceback
from ast import Break

import requests

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database


def get_reckon_vendorcredit_template(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_vendorcredit_template"]
        no_of_records = db["reckon_vendorcredit_template"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/templates/billcredit"
        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse = response.json()
        JsonResponse = list(JsonResponse)
        
        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_vendorcredit_template"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["ID"] = JsonResponse[i]["TemplateId"]
            QuerySet["Name"] = JsonResponse[i]["TemplateName"]
            arr.append(QuerySet)

        Collection.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        
