import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio


def add_excel_job(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/Job"
        excel_job = dbname['excel_job']
      
        x = excel_job.find({"job_id":job_id})
        excel_job1 = []
        for k in x:
            excel_job1.append(k)

        
        for i in range(0,len(excel_job1)):
            _id=excel_job1[i]['_id']
            task_id=excel_job1[i]['task_id']
            
            excel_job1[i].pop("_id")
            excel_job1[i].pop("job_id")
            excel_job1[i].pop("task_id")
            excel_job1[i].pop("error")
            excel_job1[i].pop("is_pushed")
            excel_job1[i].pop("payload")
            payload = json.dumps(excel_job1[i])
            asyncio.run(post_data_in_myob(url, headers, payload,excel_job,_id, job_id,task_id, excel_job1[i]["Name"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)