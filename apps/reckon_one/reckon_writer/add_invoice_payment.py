import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio



def add_excel_reckon_invoice_payment(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/receipts"
        print(url)

        excel_reckon_invoice_payment = dbname['excel_reckon_invoice_payment']
        x = excel_reckon_invoice_payment.find({"job_id":job_id})
        excel_reckon_invoice_payment1 = []
        for k in x:
            excel_reckon_invoice_payment1.append(k)

        for i in range(0,len(excel_reckon_invoice_payment1)):
            print(i)
            _id=excel_reckon_invoice_payment1[i]['_id']
            task_id=excel_reckon_invoice_payment1[i]['task_id']
            excel_reckon_invoice_payment1[i].pop("_id")
            excel_reckon_invoice_payment1[i].pop("job_id")
            excel_reckon_invoice_payment1[i].pop("task_id")
            excel_reckon_invoice_payment1[i].pop("is_pushed")
            excel_reckon_invoice_payment1[i].pop("error")
            excel_reckon_invoice_payment1[i].pop("payload")
            payload = json.dumps(excel_reckon_invoice_payment1[i])
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,excel_reckon_invoice_payment,_id, job_id,task_id, excel_reckon_invoice_payment1[i]["Reference"]))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)