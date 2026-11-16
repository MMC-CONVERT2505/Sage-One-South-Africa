import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
from apps.util.qbo_util import post_data_in_reckon
from apps.home.data_util import get_job_details, add_job_status
import asyncio
import time

def get_spend_money(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_spend_money")
        dbname = get_mongodb_database()
        Collection = dbname["sage_spend_money"]
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        
        no_of_records = dbname["sage_spend_money"].count_documents({'job_id':job_id})
        url_template = "https://accounting.sageone.co.za/api/2.0.0/AccountPayment/Get?$top=500&$skip={}&apikey={}&CompanyId={}"
        url = url_template.format(no_of_records,'{{{}}}'.format(api_key_data), company_id_data)
        response = requests.request("GET", url, headers=headers, data=payload)
        time.sleep(2)
        if response.status_code in [200,201]:
            logging.info(f"{job_id} response status-->{response.status_code}")
            JsonResponse = response.json()
            items=JsonResponse["Results"]
            arr=[]
            for item in items:

                item["job_id"]=job_id
                item["task_id"] =task_id
                item["table_name"] ="sage_spend_money"
                item["error"] =None
                item["is_pushed"] = 0
                item["payload"] = None
                arr.append(item)
        
            Collection.insert_many(arr)
            logging.info(f"{job_id} inserted many data in sage_spend_money")

            if JsonResponse["TotalResults"]!= no_of_records:
                get_spend_money(job_id,task_id)
            else:
                Break
                
        elif response.status_code == 429:
            time.sleep(3)
            print("API request limit is exceeded")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)        


def get_spend_money_contact(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_spend_money")
        dbname = get_mongodb_database()
        sage_spend_money1 = dbname["sage_spend_money"]
        sage_spend_money_contact = dbname["sage_spend_money_contact"]
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        
        sage_spend_money1 = dbname["sage_spend_money"].find({"job_id":job_id})
        contact = []
        for p1 in sage_spend_money1:
            e={}
            if "Payee" in p1:
                e['Name'] = p1['Payee']
                e['job_id'] = job_id
                e['task_id'] = task_id
                e['Date'] = p1['Date']

                start_date,end_date=get_job_details(job_id)
                if start_date <=  p1["Date"] and end_date >= p1["Date"]:
                    if e not in contact:
                        contact.append(e)
                
        sage_spend_money_contact.insert_many(contact)
        
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)        

def add_sage_spend_supplier(job_id, task_id):
    logging =log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_supplier")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        sage_supplier = dbname['sage_spend_money_contact']

        x = sage_supplier.find({"job_id": job_id})
        sage_supplier1 = []
        for k in x:
            sage_supplier1.append(k)

        for i in range(0, len(sage_supplier1)):
            _id = sage_supplier1[i]["_id"]
            QuerySet1 = {}
            QuerySet1["FirstNameBranchName"] = sage_supplier1[i].get(
                "Name", None)
            QuerySet1["SurnameBusinessName"] = sage_supplier1[i].get(
                "Name", None)
            QuerySet1["Description"] = sage_supplier1[i].get(
                "Name", None)
            QuerySet1["IsSupplier"] = True
            # QuerySet1["IsCustomer"] = True
            
            QuerySet1["IsActive"] = True


            start_date,end_date=get_job_details(job_id)

            # if start_date <=  sage_supplier1[i].get("Date") and end_date >= sage_supplier1[i].get("Date"):
                
            payload = json.dumps(QuerySet1)
            print(payload)
            asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier,
                        _id, job_id, task_id, sage_supplier1[i]["Name"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex,exc_info=True)




