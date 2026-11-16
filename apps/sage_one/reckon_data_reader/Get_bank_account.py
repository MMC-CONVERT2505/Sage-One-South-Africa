import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_reckon_bank_account(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside get _reckon_bank_account-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        collection = dbname["reckon_bank_account"]
        # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
        url = f"{base_url}/bankaccounts/1000"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        logging.info(f"{job_id} get_reckon_bank_account-->url {url}-->response.status-->{response.status_code}")
        arr = []
        for item in JsonResponse:

            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_bank_account"
            item['error'] = None
            item["is_pushed"] = 0
            arr.append(item)
                
         


        collection.insert_many(arr)
        logging.info(f"{job_id} inserted_many data in reckon_bank_account ")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex,exc_info=True)


