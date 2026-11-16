import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.log_file import log_config


def add_excel_reckon_ytd_deduction(job_id,task_id):
    print("inside add_excel_reckon_ytd_deduction ****1")
    logging = log_config(job_id)
    try:

        logging.info(f"{job_id} inside add_excel_reckon_ytd_deduction")
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/payroll/ytds/grosspays/details"
        logging.info(f"{job_id} add_excel_reckon_ytd_allowance--> url-->{url}")

        excel_reckon_deduction = dbname['get_excel_ytds_deduction']
        x = excel_reckon_deduction.find({"job_id":job_id})
        excel_reckon_deduction1 = []
        for k in x:
            excel_reckon_deduction1.append(k)
        for i in range(0,len(excel_reckon_deduction1)):
            _id=excel_reckon_deduction1[i]['_id']
            excel_reckon_deduction1[i].pop("_id")
            excel_reckon_deduction1[i].pop("job_id")
            excel_reckon_deduction1[i].pop("task_id")
            excel_reckon_deduction1[i].pop("is_pushed")
            excel_reckon_deduction1[i].pop("error")
            excel_reckon_deduction1[i].pop("payload")
            payload = json.dumps(excel_reckon_deduction1[i])

            print("payload>>>> inside write function  ***2",payload)
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,excel_reckon_deduction,_id, job_id,task_id, excel_reckon_deduction1[i]["PayItem"]))
           
                    
    except Exception as ex:
        import traceback
        traceback.print_exc()
        logging.error(ex, exc_info=True)