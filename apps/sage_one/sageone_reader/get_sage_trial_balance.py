import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config
import datetime
from datetime import datetime, timedelta

def get_sage_trial_balance(job_id,task_id):
    print("inside get sage trial balance data===========")
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside sage_trial_balance")
        dbname = get_mongodb_database()
        Collection = dbname["sage_trial_balance"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        url_template = "https://accounting.sageone.co.za/api/2.0.0/TrialBalance/Export?apikey={}&CompanyId={}"
        url = url_template.format('{{{}}}'.format(api_key_data), company_id_data)

        start_date,end_date=get_job_details(job_id)
        
        start_date_data = datetime.strptime(start_date, '%Y-%m-%d')
        new_start_date = start_date_data - timedelta(days=1)
        formatted_start_date = new_start_date.strftime('%Y-%m-%d')
        print(formatted_start_date,"formatted_start_date===========")

        date_now = datetime.strptime(start_date, '%Y-%m-%d')
        date_2 = date_now.replace(year=date_now.year - 1).strftime('%Y-%m-%d')
        

        payload1={
                "FromDate": f"{date_2}",
                "ToDate": f"{formatted_start_date}",
                        }

        response = requests.request("POST", url, headers=headers, data=payload1)
        logging.info(f"{job_id} response status-->{response.status_code}")
        JsonResponse = response.json()

       
        items=JsonResponse
        arr=[]
        for item in items:
            item["job_id"]=job_id
            item["task_id"] =task_id
            item["table_name"] ="sage_trial_balance"
            item["error"] =None
            item["is_pushed"] = 0
            item["payload"] = None
            arr.append(item)
        
        Collection.insert_many(arr)
        logging.info(f"{job_id} inserted sage trial balance function")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        


def get_sage_close_trial_balance(job_id,task_id):
    print("inside get sage trial balance data===========")
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside sage_trial_balance")
        dbname = get_mongodb_database()
        Collection = dbname["sage_close_trial_balance"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        url_template = "https://accounting.sageone.co.za/api/2.0.0/TrialBalance/Export?apikey={}&CompanyId={}"
        url = url_template.format('{{{}}}'.format(api_key_data), company_id_data)

        start_date,end_date=get_job_details(job_id)

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')


        current_start_date = start_date_obj
        while current_start_date < end_date_obj:
            current_end_date = current_start_date.replace(year=current_start_date.year + 1) - timedelta(days=1)
            if current_end_date > end_date_obj:
                current_end_date = end_date_obj

            formatted_start_date = current_start_date.strftime('%Y-%m-%d')
            formatted_end_date = current_end_date.strftime('%Y-%m-%d')

            payload1 = {
                "FromDate": formatted_start_date,
                "ToDate": formatted_end_date,
            }

            response = requests.request("POST", url, headers=headers, data=payload1)
            logging.info(f"{job_id} response status-->{response.status_code}")
            JsonResponse = response.json()

            items = JsonResponse
            arr = []
            for item in items:
                item["job_id"] = job_id
                item["task_id"] = task_id
                item["table_name"] = "sage_trial_balance"
                item["error"] = None
                item["is_pushed"] = 0
                item["payload"] = None
                arr.append(item)

            Collection.insert_many(arr)
            logging.info(f"{job_id} inserted sage trial balance function for period {formatted_start_date} to {formatted_end_date}")


            current_start_date = current_end_date + timedelta(days=1)

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
