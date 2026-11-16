import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.log_file import log_config


def add_excel_leave_entitlement(job_id,task_id):
    print("inside  add_excel_leave_entitlement****1")
    logging = log_config(job_id)
    try:

        logging.info(f"{job_id} inside add_excel_leave_entitlement")
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/payroll/contacts"
        logging.info(f"{job_id} add_excel_leave_entitlement--> url-->{url}")

        leave_entitlement = dbname["excel_reckon_leave_entitlements"]
        x = leave_entitlement.find({"job_id":job_id})
        leave_entitlement1 = []
        for k in x:
            leave_entitlement1.append(k)
        print("bgbvbgy",leave_entitlement1)
        for i in range(0,len(leave_entitlement1)):
            _id=leave_entitlement1[i]['_id']
            task_id=leave_entitlement1[i]['task_id']
            leave_entitlement1[i].pop("_id")
            leave_entitlement1[i].pop("job_id")
            leave_entitlement1[i].pop("task_id")
            leave_entitlement1[i].pop("is_pushed")
            leave_entitlement1[i].pop("error")
            leave_entitlement1[i].pop("payload")
            payload = json.dumps(leave_entitlement1[i])

            print("payload>>>> inside write function  ***2",payload)
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,leave_entitlement,_id, job_id,task_id, leave_entitlement1[i]["FirstNameBranchName"]))
           

    except Exception as ex:
        import traceback
        traceback.print_exc()
        logging.error(ex, exc_info=True)