import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.log_file import log_config


def add_excel_reckon_leave_balance(job_id,task_id):
    print("inside add_excel_reckon_leave_balance ****1")
    logging = log_config(job_id)
    try:

        logging.info(f"{job_id} inside add_excel_reckon_leave_balance")
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/payroll/ytds/leavebalances/details"
        logging.info(f"{job_id} add_excel_reckon_leave_balance--> url-->{url}")

        excel_reckon_leave_balance = dbname['excel_reckon_leave_balance']
        x = excel_reckon_leave_balance.find({"job_id":job_id})
        excel_reckon_leave1_balance = []
        for k in x:
            excel_reckon_leave1_balance.append(k)
        print(excel_reckon_leave1_balance)
        for i in range(0,len(excel_reckon_leave1_balance)):
            # print(excel_reckon_leave1_balance[0]['list'])
            _id=excel_reckon_leave1_balance[i]['_id']
            excel_reckon_leave1_balance[i].pop("_id")
            excel_reckon_leave1_balance[i].pop("job_id")
            excel_reckon_leave1_balance[i].pop("task_id")
            excel_reckon_leave1_balance[i].pop("is_pushed")
            excel_reckon_leave1_balance[i].pop("error")
            excel_reckon_leave1_balance[i].pop("payload")
            # print(excel_reckon_leave1_balance)
            payload = json.dumps(excel_reckon_leave1_balance[i])

            print("payload>>>> inside write function  ***2",payload)
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,excel_reckon_leave_balance,_id, job_id,task_id, excel_reckon_leave1_balance[i]["PayItem"]))
           
                    
    except Exception as ex:
        import traceback
        traceback.print_exc()
        logging.error(ex, exc_info=True)