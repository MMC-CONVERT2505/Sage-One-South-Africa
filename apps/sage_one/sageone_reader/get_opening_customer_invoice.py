import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
from apps.home.data_util import get_job_details


def get_opening_customer_invoice(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_bill")
        dbname = get_mongodb_database()
        sage_AR_customer = dbname["sage_AR_customer"]
        payload, headers, api_key_data, company_id_data = get_settings_sageone(
            job_id)

        sage_opening_cust = dbname['sage_opening_customer']

        x = sage_opening_cust.find({"job_id": job_id, "is_pushed": 0})
        sage_opening_cust1 = []
        for k in x:
            sage_opening_cust1.append(k)

        # url_template = "https://accounting.sageone.com.au/api/1.1.2/CustomerOpeningBalance/Get?&includeDetail=true&apikey={}&CompanyId={}"
        # url = url_template.format(
        #     '{{{}}}'.format(api_key_data), company_id_data)
        


        # for i in range(0, len(sage_opening_cust1)):
        #     print(sage_opening_cust1[i],"payload data==========")
            

        #     data1={}

        #     data1["CustomerId"]=sage_opening_cust1[i]["CustomerId"]

        #     payload = json.dumps(data1)
        #     print(payload,"payload data-3-23242389423")
        #     print(url,"url-------")
        #     print(headers,"headers---838338")


        #     response = requests.request("POST", url, headers=headers, data=payload)
        #     print(response,"response data chjdss09009")
            # logging.info(f"{job_id} response status --> {response.status_code}")
            # JsonResponse = response.json()
            # items = JsonResponse["Results"]

            # arr = []
            # for item in items:
            #     item["job_id"] = job_id
            #     item["task_id"] = task_id
            #     item["table_name"] = "sage_opening_customer"
            #     item["error"] = None
            #     item["is_pushed"] = 0
            #     item["payload"] = None
            #     arr.append(item)
            #     Collection.insert_many(arr)


        import requests
        import json

        url = "https://accounting.sageone.com.au/api/1.1.2/OutstandingCustomerDocument/Get?includeDetail=true&apikey={C843A051-A7A3-42C6-9CF9-0B742EE28D50}&CompanyId=4975"


        for i in range(0, len(sage_opening_cust1)):
            print(sage_opening_cust1[i],"payload data==========")
            

            data1={}

            data1["CustomerId"]=sage_opening_cust1[i]["CustomerId"]

            # payload = json.dumps(data1)

            payload = json.dumps(data1)
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic cmVja29uY2xpZW50c0BtbWNjb252ZXJ0LmNvbTpBbmtpdEAyNTA1',
            'Cookie': '__cf_bm=.Ebf3bpzyK7FJBrOq430_RxIxRG_26P0KlVcjcLXrh8-1713408422-1.0.1.1-UK27RugaAJeDF2SBp6BLakXHxCS9SX84E8RHCzyAz2prBQyDNN.K6x6yyVXHSjZUzFMxLbR9J1J7RFrFpvOeBg'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            JsonResponse = response.json()
            items = JsonResponse["Results"]
            print(items,"items data ==========")

            arr = []
            for item in items:
                item["job_id"] = job_id
                item["task_id"] = task_id
                item["table_name"] = "sage_AR_customer"
                item["error"] = None
                item["is_pushed"] = 0
                item["payload"] = None
                arr.append(item)
            sage_AR_customer.insert_many(arr)



           
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
