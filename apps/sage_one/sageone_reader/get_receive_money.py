import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
import asyncio
from apps.util.qbo_util import post_data_in_reckon
from apps.home.data_util import get_job_details, add_job_status
import time



def get_receive_money(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_receive_money")
        dbname = get_mongodb_database()
        Collection = dbname["sage_receive_money"]
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        
        no_of_records = dbname["sage_receive_money"].count_documents({'job_id':job_id})
        url_template = "https://accounting.sageone.co.za/api/2.0.0/AccountReceipt/Get?$top=500&$skip={}&apikey={}&CompanyId={}"
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
                item["table_name"] ="sage_receive_money"
                item["error"] =None
                item["is_pushed"] = 0
                item["payload"] = None
                arr.append(item)

        
            Collection.insert_many(arr)
            logging.info(f"{job_id} inserted many data in sage_receive_money")

            if JsonResponse["TotalResults"]!= no_of_records:
                get_receive_money(job_id,task_id)
            else:
                Break

        elif response.status_code == 429:
            time.sleep(3)
            print("API request limit is exceeded")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)        


def get_receive_money_contact(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_receive_money")
        dbname = get_mongodb_database()
        sage_receive_money1 = dbname["sage_receive_money"]
        sage_receive_money_contact = dbname["sage_receive_money_contact"]
        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)
        
        sage_receive_money1 = dbname["sage_receive_money"].find({"job_id":job_id})
        contact = []
        for p1 in sage_receive_money1:
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
        

            
        sage_receive_money_contact.insert_many(contact)
        
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)        

def add_sage_receive_customer(job_id, task_id):
    logging =log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_sage_receive_customer")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        sage_customer = dbname['sage_receive_money_contact']

        x = sage_customer.find({"job_id": job_id})
        sage_customer1 = []
        for k in x:
            sage_customer1.append(k)

        for i in range(0, len(sage_customer1)):
            _id = sage_customer1[i]["_id"]
            QuerySet1 = {}
            QuerySet1["FirstNameBranchName"] = sage_customer1[i].get(
                "Name", None)
            QuerySet1["SurnameBusinessName"] = sage_customer1[i].get(
                "Name", None)
            QuerySet1["Description"] = sage_customer1[i].get(
                "Name", None)
            QuerySet1["IsCustomer"] = True
            # QuerySet1["IsSupplier"] = True
            QuerySet1["IsActive"] = True

            start_date,end_date=get_job_details(job_id)

            # if start_date <=  sage_customer1[i].get("Date") and end_date >= sage_customer1[i].get("Date"):
        
            payload = json.dumps(QuerySet1)
            asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer,
                        _id, job_id, task_id, sage_customer1[i]["Name"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex,exc_info=True)



def get_common_contact(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_receive_money")
        dbname = get_mongodb_database()

        sage_comman_contact = dbname["sage_comman_contact"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        reckon_supplier = dbname['reckon_supplier']

        x = reckon_supplier.find({"job_id": job_id})
        reckon_supplier1 = []
        for k in x:
            reckon_supplier1.append(k)

        sage_receive_money_contact = dbname['sage_receive_money_contact']
        x = sage_receive_money_contact.find({"job_id": job_id})
        sage_receive_money_contact1 = []
        for k in x:
            sage_receive_money_contact1.append(k)

        arr = []
        for i in range(0,len(reckon_supplier1)):
            for j in range(0,len(sage_receive_money_contact1)):
                if reckon_supplier1[i]["Description"].lower().strip()== sage_receive_money_contact1[j]["Name"].lower().strip():
                    
                    e={}
                    e['Name'] = reckon_supplier1[i]['Description']
                    e['job_id'] = job_id
                    e['task_id'] = task_id
                    if e not in arr:
                        arr.append(e)


        print(arr,"contact=====")

            # print(contact,"contact dta=====")
            
        sage_comman_contact.insert_many(arr)
        
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)    

# def get_comman_contact(job_id, task_id):   
#     logging = log_config(job_id) 
#     try:
#         logging.info(f"{job_id} inside get_common_contact")
#         dbname = get_mongodb_database()

#         comman_contact = dbname["sage_common_contact"]

#         payload, headers, api_key_data, company_id_data = get_settings_sageone(job_id)

#         reckon_supplier = dbname['reckon_supplier']
#         sage_receive_money_contact = dbname['sage_receive_money_contact']

#         reckon_supplier_data = list(reckon_supplier.find({"job_id": job_id}))
#         sage_receive_money_contact_data = list(sage_receive_money_contact.find({"job_id": job_id}))

#         for reckon_supplier_record in reckon_supplier_data:
            
#             for sage_receive_money_contact_record in sage_receive_money_contact_data:
#                 contact = []
#                 if sage_receive_money_contact_record["Name"].lower().strip() == reckon_supplier_record["Description"].lower().strip():
                    
#                     contact.append({
#                         'Name': reckon_supplier_record['Description'],
#                         'job_id': job_id,
#                         'task_id': task_id
#                     })
                
#             if contact:
#                 comman_contact.insert_many(contact)

#     except Exception as ex:
#         traceback.print_exc()
#         logging.error(ex, exc_info=True)





def get_common_contact_customer(job_id,task_id):   
    logging = log_config(job_id) 
    try:
        logging.info(f"{job_id} inside get_receive_money_contact")
        dbname = get_mongodb_database()

        sage_comman_contact = dbname["sage_comman_contact_customer"]

        payload, headers,api_key_data,company_id_data= get_settings_sageone(job_id)

        reckon_customer = dbname['reckon_customer']

        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)

        sage_spend_money_contact = dbname['sage_spend_money_contact']
        x = sage_spend_money_contact.find({"job_id": job_id})
        sage_spend_money_contact1 = []
        for k in x:
            sage_spend_money_contact1.append(k)

        arr = []
        for i in range(0,len(reckon_customer1)):
            for j in range(0,len(sage_spend_money_contact1)):
                if reckon_customer1[i]["Description"].lower().strip()== sage_spend_money_contact1[j]["Name"].lower().strip():
                    
                    e={}
                    e['Name'] = reckon_customer1[i]['Description']
                    e['job_id'] = job_id
                    e['task_id'] = task_id
                    if e not in arr:
                        arr.append(e)


        print(arr,"contact=====")

            # print(contact,"contact dta=====")
            
        sage_comman_contact.insert_many(arr)
        
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)  