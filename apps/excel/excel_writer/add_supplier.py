import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio


def add_excel_supplier(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers = get_settings_myob(job_id)

        url = f"{base_url}/Contact/Supplier"

        excel_supplier = dbname['excel_supplier']
        taxcode_myob = dbname['taxcode_myob']

        x = excel_supplier.find({"job_id":job_id})
        excel_supplier1 = []
        for k in x:
            excel_supplier1.append(k)

        s = taxcode_myob.find({"job_id":job_id})
        taxcode_myob1 = []
        for k in s:
            taxcode_myob1.append(k)
        
        for i in range(0,len(excel_supplier1)):
            _id=excel_supplier1[i]['_id']
            task_id=excel_supplier1[i]['task_id']
            
            excel_supplier1[i].pop("_id")
            excel_supplier1[i].pop("job_id")
            excel_supplier1[i].pop("task_id")
            excel_supplier1[i].pop("is_pushed")
            excel_supplier1[i].pop("payload")
            payload = json.dumps(excel_supplier1[i])
            print(payload)
            print("------------")
            asyncio.run(post_data_in_myob(url, headers, payload,excel_supplier,_id, job_id,task_id, excel_supplier1[i]["CompanyName"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)