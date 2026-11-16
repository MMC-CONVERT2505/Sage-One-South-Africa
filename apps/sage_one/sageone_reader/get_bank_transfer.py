import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import time
from apps.home.data_util import get_job_details

def get_bank_transfer(job_id,task_id):
    logging = log_config(job_id)
    try:
        start_date, end_date = get_job_details(job_id)
        logging.info(f"{job_id} inside get_bank_transfer")
        dbname = get_mongodb_database()
        Collection = dbname["sage_bank_transfer"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        no_of_records = dbname["sage_bank_transfer"].count_documents({'job_id':job_id})
        url_template = "https://accounting.sageone.co.za/api/2.0.0/BankTransaction/Get?$top=500&$skip={}&apikey={}&CompanyId={}"
        url = url_template.format(no_of_records,'{{{}}}'.format(api_key_data), company_id_data)
        print(url)
        response = requests.request("GET", url, headers=headers, data=payload)
        time.sleep(1)
        if response.status_code in [200,201]:
            logging.info(f"{job_id} response status --->{response.status_code}")
            JsonResponse = response.json()
            items=JsonResponse["Results"]
            arr=[]
            for item in items:
                item.pop('$dirty', None)
                item["job_id"]=job_id
                item["task_id"] =task_id
                item["table_name"] ="sage_bank_transfer"
                item["error"] =None
                item["is_pushed"] = 0
                item["payload"] = None


                # date_str = item["Date"]
                # date = date_str.split("T")[0]  
                # print(date,"date =========")

                # if start_date <= date and end_date >= date:
                # if item["Type"] == 4:
                arr.append(item)

            
            Collection.insert_many(arr)
            logging.info(f"{job_id} inserted many data in sage_bank_transfer")

            if JsonResponse["TotalResults"]!= no_of_records:
                get_bank_transfer(job_id,task_id)
            else:
                Break
        elif response.status_code == 429:
            time.sleep(3)
            print("API request limit is exceeded")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        


