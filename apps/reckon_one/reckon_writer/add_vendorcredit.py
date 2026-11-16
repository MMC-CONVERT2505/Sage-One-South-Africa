import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio


def add_excel_reckon_vendorcredit(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/suppliercreditnotes"
        print(url)

        excel_reckon_vendorcredit = dbname['excel_reckon_vendorcredit']
        x = excel_reckon_vendorcredit.find({"job_id":job_id})
        excel_reckon_vendorcredit1 = []
        for k in x:
            excel_reckon_vendorcredit1.append(k)

        for i in range(0,len(excel_reckon_vendorcredit1)):
            print(i)
            _id=excel_reckon_vendorcredit1[i]['_id']
            task_id=excel_reckon_vendorcredit1[i]['task_id']
            excel_reckon_vendorcredit1[i].pop("_id")
            excel_reckon_vendorcredit1[i].pop("job_id")
            excel_reckon_vendorcredit1[i].pop("task_id")
            excel_reckon_vendorcredit1[i].pop("is_pushed")
            excel_reckon_vendorcredit1[i].pop("error")
            excel_reckon_vendorcredit1[i].pop("payload")
            # for j in range (0,len(excel_reckon_vendorcredit1[i]['LineItems'])):
            #     excel_reckon_vendorcredit1[i]['LineItems'][j].pop("AccountName")
            #     excel_reckon_vendorcredit1[i]['LineItems'][j].pop("Item")
            #     excel_reckon_vendorcredit1[i]['LineItems'][j].pop("Account")
            
            payload = json.dumps(excel_reckon_vendorcredit1[i])
            print(payload)
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,excel_reckon_vendorcredit,_id, job_id,task_id, excel_reckon_vendorcredit1[i]["Reference"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)