import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_customer_adjustment(job_id,task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_customer_adjustment")
        print("inside get customer ")
        dbname = get_mongodb_database()
        Collection = dbname["sage_customer_adjustment"]

        no_of_records = dbname["sage_customer_adjustment"].count_documents({'job_id':job_id})
       
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        url_template = "https://accounting.sageone.co.za/api/2.0.0/CustomerAdjustment/Get?$top=500&$skip={}&includeDetail=true&apikey={}&CompanyId={}"
        url = url_template.format(no_of_records,'{{{}}}'.format(api_key_data), company_id_data)
       

        logging.info(url)
        # url = url_template.format('{{{}}}'.format(api_key_data), company_id_data)

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code in [200,201]:
            logging.info(f"{job_id} response status -->{response.status_code}")
            JsonResponse = response.json()
            items=JsonResponse["Results"]
            arr=[]
            for item in items:
                item["job_id"]=job_id
                item["task_id"] =task_id
                item["table_name"] ="sage_customer_adjustment"
                item["error"] =None
                item["is_pushed"] = 0
                item["payload"] = None
                arr.append(item)
            
            Collection.insert_many(arr)
            logging.info(f"{job_id} inserted many data in sage_customer_adjustment")

        if JsonResponse["TotalResults"]!= no_of_records:
            get_customer_adjustment(job_id,task_id)
        else:
            Break



    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        


