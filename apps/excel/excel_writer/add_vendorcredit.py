import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio




def add_excel_vendorcredit(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)
        excel_vendorcredit = dbname['excel_vendorcredit']
        
        x = excel_vendorcredit.find({"job_id":job_id})
        excel_vendorcredit1 = []
        for k in x:
            excel_vendorcredit1.append(k)

        for i in range(0,len(excel_vendorcredit1)):
            print(excel_vendorcredit1[i]['Number'])
            _id=excel_vendorcredit1[i]['_id']
            task_id = excel_vendorcredit1[i]['task_id']

            excel_vendorcredit1[i].pop("_id")
            excel_vendorcredit1[i].pop("job_id")
            excel_vendorcredit1[i].pop("task_id")
            excel_vendorcredit1[i].pop("is_pushed")
            excel_vendorcredit1[i].pop("error")
            excel_vendorcredit1[i].pop("payload")
            payload = json.dumps(excel_vendorcredit1[i])
            
            url1 = f"{base_url}/Purchase/Bill/Item"
            asyncio.run(
            post_data_in_myob(url1, headers, payload, excel_vendorcredit, _id, job_id, task_id,
                                excel_vendorcredit1[i]["Number"]))
                


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)