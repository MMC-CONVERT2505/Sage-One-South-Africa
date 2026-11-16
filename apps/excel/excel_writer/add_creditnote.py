import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio



def add_excel_creditnote(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        excel_creditnote = dbname['excel_creditnote']
      
        x = excel_creditnote.find({"job_id":job_id})
        excel_creditnote1 = []
        for k in x:
            excel_creditnote1.append(k)

        
        for i in range(0,len(excel_creditnote1)):
            _id=excel_creditnote1[i]['_id']
            task_id=excel_creditnote1[i]['task_id']
            
            excel_creditnote1[i].pop("_id")
            excel_creditnote1[i].pop("job_id")
            excel_creditnote1[i].pop("error")
            excel_creditnote1[i].pop("task_id")
            excel_creditnote1[i].pop("is_pushed")
            excel_creditnote1[i].pop("payload")
            payload1 = json.dumps(excel_creditnote1[i])

            payload, base_url, headers = get_settings_myob(job_id)

            url = f"{base_url}/Sale/Invoice/Item"
            
            asyncio.run(post_data_in_myob(url, headers, payload1,excel_creditnote,_id, job_id,task_id, excel_creditnote1[i]["Number"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)