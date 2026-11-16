import json
import requests
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_myob
import asyncio



def add_excel_bill_payment(job_id,task_id):
    try:
        dbname=get_mongodb_database()
        payload={}
        excel_bill_payment = dbname['excel_bill_payment']
      
        x = excel_bill_payment.find({"job_id":job_id})
        excel_bill_payment1 = []
        for k in x:
            excel_bill_payment1.append(k)

        
        for i in range(0,len(excel_bill_payment1)):
            _id=excel_bill_payment1[i]['_id']
            task_id=excel_bill_payment1[i]['task_id']
            billnumber=str(excel_bill_payment1[i]["BillNumber"])
            
            excel_bill_payment1[i].pop("_id")
            excel_bill_payment1[i].pop("job_id")
            excel_bill_payment1[i].pop("task_id")
            excel_bill_payment1[i].pop("is_pushed")
            excel_bill_payment1[i].pop("error")
            excel_bill_payment1[i].pop("BillNumber")
            excel_bill_payment1[i].pop("payload")
            payload = json.dumps(excel_bill_payment1[i])

            payload1, base_url, headers = get_settings_myob(job_id)
            id_or_name_value_for_error = str(excel_bill_payment1[i]["PaymentNumber"])+"-"+billnumber
            url = f"{base_url}/Purchase/SupplierPayment"
            asyncio.run(
                post_data_in_myob(url, headers, payload,excel_bill_payment,_id, job_id,task_id,id_or_name_value_for_error ))


    except Exception as ex:
        print("------------------------------")
        import traceback
        traceback.print_exc()
        print(ex)