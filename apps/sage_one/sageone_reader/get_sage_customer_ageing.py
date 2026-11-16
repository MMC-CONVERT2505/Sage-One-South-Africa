import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config

def get_sage_customer_ageing(job_id,task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside sage_customer_ageing")
        dbname = get_mongodb_database()
        Collection = dbname["sage_customer_ageing"]

        no_of_records = dbname["sage_customer_ageing"].count_documents({'job_id':job_id})
        
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        url_template = "https://accounting.sageone.co.za/api/2.0.0/CustomerAgeing/GetDetail?$top=500&$skip={}&apikey={}&CompanyId={}"
        url = url_template.format(no_of_records,'{{{}}}'.format(api_key_data), company_id_data)
        
        start_date,end_date=get_job_details(job_id)
        print(start_date,"start_date=======")

        from datetime import datetime, timedelta
        start_date_data = datetime.strptime(start_date, '%Y-%m-%d')
        new_start_date = start_date_data - timedelta(days=1)
        formatted_start_date = new_start_date.strftime('%Y-%m-%d')
        print(formatted_start_date,"formatted_start_date===========")

        payload1={
                "ToDate": f"{formatted_start_date}"
                }

        response = requests.request("POST", url, headers=headers, data=payload1)
        logging.info(f"{job_id} response status-->{response.status_code}")
        JsonResponse = response.json()

        print(JsonResponse,"jsonresponse data===============")

        items=JsonResponse["Results"]
        arr=[]
        for item in items:
            item["job_id"]=job_id
            item["task_id"] =task_id
            item["table_name"] ="sage_analysis_type"
            item["error"] =None
            item["is_pushed"] = 0
            item["payload"] = None
            arr.append(item)

        Collection.insert_many(arr)
        logging.info(f"{job_id} inserted many data in sage_tax")
        
        if JsonResponse["TotalResults"]!= no_of_records:
            get_sage_customer_ageing(job_id,task_id)
        else:
            Break
        

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        


