import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config
import datetime
import json
from datetime import datetime, timedelta


def get_reckon_report_trial_balance_second_years(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_report_trial_balance_current"]
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/reports/trialbalance/false"
        print(url,"url ------")

        start_date,end_date=get_job_details(job_id)
        
        date_now = datetime.strptime(start_date, '%Y-%m-%d')

        date_2 = date_now.replace(year=date_now.year + 1)
        payload1 =json.dumps({
            "Orientation": "Portrait",
            "ReportingBasis": "AccrualsBasis",
            "PeriodFilter": {
                "PeriodType": "Custom",
                "StartDay": f"{date_2}",
                "EndDay": f"{end_date}"
            }

        })

        print(payload1,"payload1=============")

        print(get_headers,"get_headers=============")

        response = requests.request("POST", url, headers=get_headers, data=payload1)
        JsonResponse1 = response.json()

       

        print(JsonResponse1)

    
        arr=[]
        JsonResponse1["job_id"]=job_id
        JsonResponse1["task_id"] =task_id
        JsonResponse1["table_name"] ="reckon_trial_balance"
        JsonResponse1["error"] =None
        JsonResponse1["is_pushed"] = 0
        JsonResponse1["payload"] = None
        arr.append(JsonResponse1)
    
        Collection.insert_many(arr)
        

    except Exception as ex:
        traceback.print_exc()



