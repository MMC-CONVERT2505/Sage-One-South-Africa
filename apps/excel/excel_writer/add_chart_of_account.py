import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio



def add_excel_chart_of_account(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/GeneralLedger/Account"

        excel_coa = dbname['excel_chart_of_account']
      
        x = excel_coa.find({"job_id":job_id})
        excel_coa1 = []
        for k in x:
            excel_coa1.append(k)

        coa1 = dbname['chart_of_account'].find({"job_id":job_id})
        coa = []
        for k1 in coa1:
            coa.append(k1)


        excel_coa1=excel_coa1
        
        for i in range(0,len(excel_coa1)):
            payload, base_url, headers = get_settings_myob(job_id)

            parentaccount={}
                
            for j in range(0,len(coa)):
                if excel_coa1[i]["ParentAccount"] == coa[j]['DisplayId']:
                    parentaccount["UID"] = coa[j]['UID']
                    parentaccount["Name"] = coa[j]['Name']
                    parentaccount["DisplayID"] = coa[j]['DisplayId']
        
            _id=excel_coa1[i]['_id']
            task_id=excel_coa1[i]['task_id']
            excel_coa1[i].pop("_id")
            excel_coa1[i].pop("ParentAccount")
            excel_coa1[i].pop("job_id")
            excel_coa1[i].pop("task_id")
            excel_coa1[i].pop("is_pushed")
            excel_coa1[i].pop("error")
            excel_coa1[i].pop("payload")
            excel_coa1[i]['ParentAccount'] = parentaccount

            payload = json.dumps(excel_coa1[i])
            print(payload)
            print("---")
            asyncio.run(post_data_in_myob(url, headers, payload,excel_coa,_id, job_id,task_id, excel_coa1[i]["Name"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)