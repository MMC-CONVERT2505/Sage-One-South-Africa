import json
import requests
import asyncio
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob



def add_excel_bill(job_id,task_id):
    
    try:
        dbname=get_mongodb_database()
        # payload, base_url, headers = get_settings_myob(job_id)
        payload ={}


        excel_bill = dbname['excel_bill']
        
        x = excel_bill.find({"job_id":job_id})
        excel_bill1 = []
        for k in x:
            excel_bill1.append(k)

        for i in range(0,len(excel_bill1)):
            print(i)
            _id=excel_bill1[i]['_id']
            task_id = excel_bill1[i]['task_id']

            
            excel_bill1[i].pop("_id")
            excel_bill1[i].pop("job_id")
            excel_bill1[i].pop("task_id")
            excel_bill1[i].pop("is_pushed")
            excel_bill1[i].pop("error")
            excel_bill1[i].pop("payload")
            payload = json.dumps(excel_bill1[i])
          
            payload1, base_url, headers = get_settings_myob(job_id)
            url1 = f"{base_url}/Purchase/Bill/Item"
            asyncio.run(
                post_data_in_myob(url1, headers, payload, excel_bill, _id, job_id, task_id,
                excel_bill1[i]["Number"])
            )
    

            # for j in range(0, len(excel_bill1[i]["Lines"])):
            #     if excel_bill1[i]["Lines"][j]["Item"] != None:
            #         url1 = f"{base_url}/Purchase/Bill/Item"
            #         post_data_in_myob(url1, headers, payload, excel_bill, _id, job_id, task_id,
            #                           excel_bill1[i]["Number"])
            #     else:
            #         url1 = f"{base_url}/Purchase/Bill/Service"
            #         post_data_in_myob(url1, headers, payload, excel_bill, _id, job_id, task_id,
            #                           excel_bill1[i]["Number"])


            
    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)
