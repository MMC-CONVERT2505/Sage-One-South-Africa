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

def get_sage_report_trial_balance(job_id,task_id):
    print("inside get sage report trial balance data===========")
    try:
        dbname = get_mongodb_database()
        Collection = dbname["sage_report_trial_balance"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        url_template = "https://accounting.sageone.co.za/api/2.0.0/TrialBalance/Export?apikey={}&CompanyId={}"
        url = url_template.format('{{{}}}'.format(api_key_data), company_id_data)

        start_date,end_date=get_job_details(job_id)
        
        
        date_now = datetime.strptime(start_date, '%Y-%m-%d')

        date_2 = date_now.replace(year=date_now.year + 1)
        new_start_date = date_2 - timedelta(days=1)
        

        payload1={
                "FromDate": f"{start_date}",
                "ToDate": f"{new_start_date}",
                "DisplayReportingGroupDetail": True,
                "Comparative": True,
                "CurrencyId": 1
                }

        response = requests.request("POST", url, headers=headers, data=payload1)
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
        return True

    except Exception as ex:
        traceback.print_exc()
        # logging.error(ex, exc_info=True)
        


