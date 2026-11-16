import os
import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon, get_settings_reckon_v2
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_reckon_item(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside get_reckon_item-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        collection = dbname["reckon_item"]
        # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
        url = f"{base_url}/items/100000"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_reckon_item--> url -->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        arr = []
        for item in JsonResponse:

            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_item"
            item['error'] = None
            item["is_pushed"] = 0

            arr.append(item)
            
        collection.insert_many(arr)
        logging.info(f"{job_id} inserted many data in reckon_item")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)




# The rest of your code...
def get_reckon_item_history(job_id, task_id):
    logging = log_config(job_id)

    try:
        logging.info(f"{job_id} inside get_reckon_item_history-------------updated")

        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon_v2(job_id)

        collection = dbname["reckon_item_history"]

        url = f"{base_url}/items"
        response = requests.get(url, headers=get_headers)
        print(response.status_code)

        logging.info(
            f"{job_id} get_reckon_item_history --> url --> {url} "
            f"response status --> {response.status_code}"
        )

        items = response.json().get("list", [])
        print(items)
        arr = []

        for item in items:
            created_dt = item.get("createdDateTime")
            modified_dt = item.get("lastModifiedDateTime")


            if not created_dt or not modified_dt:
                continue


            if created_dt == modified_dt:
                continue

            # enrich record
            item.update({
                "job_id": job_id,
                "task_id": task_id,
                "table_name": "reckon_item_history",
                "error": None,
                "is_pushed": 0
            })

            arr.append(item)

        if arr:
            collection.insert_many(arr)
            logging.info(f"{job_id} inserted {len(arr)} modified records into reckon_item_history")
        else:
            logging.info(f"{job_id} no modified records found")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)






import pandas as pd
import traceback
import requests

def get_reckon_item_excel(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside get_reckon_item-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)
        collection = dbname["reckon_excel_item"]
        
        url = f"{base_url}/items/100000"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_reckon_item--> url -->{url} response status-->{response.status_code}")
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1.get('Items', [])

        arr = []
        for item in JsonResponse:
            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_item"
            item['error'] = None
            item["is_pushed"] = 0
            arr.append(item)

        if arr:
            # Insert into MongoDB
            collection.insert_many(arr)
            logging.info(f"{job_id} inserted many data in reckon_item")

            # Export to Excel
            df = pd.DataFrame(arr)
            os.makedirs("output", exist_ok=True)
            excel_file_path = os.path.join("output", f"reckon_item_{job_id}.xlsx")

            df.to_excel(excel_file_path, index=False)
            logging.info(f"{job_id} Excel file created at {excel_file_path}")

        else:
            logging.warning(f"{job_id} No data found in Reckon response.")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
