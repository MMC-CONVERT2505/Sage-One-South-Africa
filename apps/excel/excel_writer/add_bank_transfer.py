import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio




def add_excel_bank_transfer(job_id, task_id):
    try:
        dbname=get_mongodb_database()
        
        excel_bank_transfer = dbname['excel_bank_transfer']
        taxcode_myob = dbname['taxcode_myob']

        x = excel_bank_transfer.find({"job_id":job_id})
        excel_bank_transfer1 = []
        for k in x:
            excel_bank_transfer1.append(k)

        
        for i in range(0,len(excel_bank_transfer1)):
            _id=excel_bank_transfer1[i]['_id']
            task_id=excel_bank_transfer1[i]['task_id']
            excel_bank_transfer1[i].pop("_id")
            excel_bank_transfer1[i].pop("job_id")
            excel_bank_transfer1[i].pop("task_id")
            excel_bank_transfer1[i].pop("is_pushed")
            excel_bank_transfer1[i].pop("error")
            excel_bank_transfer1[i].pop("payload")
            payload = json.dumps(excel_bank_transfer1[i])
            payload1, base_url, headers = get_settings_myob(job_id)

            url = f"{base_url}/Banking/TransferMoneyTxn"
        
            
            asyncio.run(post_data_in_myob(url, headers, payload,excel_bank_transfer,_id, job_id,task_id, excel_bank_transfer1[i]["TransferNumber"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)