import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio




def add_excel_invoice_payment(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        excel_invoice_payment = dbname['excel_invoice_payment']
      
        x = excel_invoice_payment.find({"job_id":job_id})
        excel_invoice_payment1 = []
        for k in x:
            excel_invoice_payment1.append(k)

        
        for i in range(0,len(excel_invoice_payment1)):
            print(excel_invoice_payment1[i]['ReceiptNumber'])
            _id=excel_invoice_payment1[i]['_id']
            task_id=excel_invoice_payment1[i]['task_id']
            invnumber = excel_invoice_payment1[i]['invnumber']
            
            excel_invoice_payment1[i].pop("_id")
            excel_invoice_payment1[i].pop("job_id")
            excel_invoice_payment1[i].pop("error")
            excel_invoice_payment1[i].pop("invnumber")
            excel_invoice_payment1[i].pop("task_id")
            excel_invoice_payment1[i].pop("is_pushed")
            excel_invoice_payment1[i].pop("payload")
            payload1 = json.dumps(excel_invoice_payment1[i])
            print(payload1)
            print("------------")
            payload, base_url, headers = get_settings_myob(job_id)

            url = f"{base_url}/Sale/CustomerPayment"
            id_or_name_value_for_error= invnumber
            asyncio.run(post_data_in_myob(url, headers, payload1,excel_invoice_payment,_id, job_id,task_id,id_or_name_value_for_error ))

    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)