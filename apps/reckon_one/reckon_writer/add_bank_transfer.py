import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio


def add_excel_reckon_bank_transfer(job_id, task_id):
    try:
        dbname=get_mongodb_database()
        
        excel_reckon_bank_transfer = dbname['excel_reckon_bank_transfer']
        taxcode_myob = dbname['taxcode_myob']

        x = excel_reckon_bank_transfer.find({"job_id":job_id})
        excel_reckon_bank_transfer1 = []
        for k in x:
            excel_reckon_bank_transfer1.append(k)

        
        for i in range(0,len(excel_reckon_bank_transfer1)):
            _id=excel_reckon_bank_transfer1[i]['_id']
            task_id=excel_reckon_bank_transfer1[i]['task_id']
            excel_reckon_bank_transfer1[i].pop("_id")
            excel_reckon_bank_transfer1[i].pop("job_id")
            excel_reckon_bank_transfer1[i].pop("task_id")
            excel_reckon_bank_transfer1[i].pop("is_pushed")
            excel_reckon_bank_transfer1[i].pop("error")
            excel_reckon_bank_transfer1[i].pop("payload")
            payload1 = json.dumps(excel_reckon_bank_transfer1[i])
            payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

            url = f"{base_url}/banktransfers"
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload1,excel_reckon_bank_transfer,_id, job_id,task_id, excel_reckon_bank_transfer1[i]["Amount"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)