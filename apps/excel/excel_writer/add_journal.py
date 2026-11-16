import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio




def add_excel_journal(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        excel_journal = dbname['excel_journal']
      
        x = excel_journal.find({"job_id":job_id})
        excel_journal1 = []
        for k in x:
            excel_journal1.append(k)

        
        for i in range(0,len(excel_journal1)):
            _id=excel_journal1[i]['_id']
            task_id=excel_journal1[i]['task_id']
            
            excel_journal1[i].pop("_id")
            excel_journal1[i].pop("job_id")
            excel_journal1[i].pop("task_id")
            excel_journal1[i].pop("is_pushed")
            excel_journal1[i].pop("error")
            excel_journal1[i].pop("payload")
            payload = json.dumps(excel_journal1[i])
            print(payload)
            print("------------")
            payload1, base_url, headers = get_settings_myob(job_id)

            url = f"{base_url}/GeneralLedger/GeneralJournal"
        
            asyncio.run(post_data_in_myob(url, headers, payload,excel_journal,_id, job_id,task_id, excel_journal1[i]["DisplayID"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)