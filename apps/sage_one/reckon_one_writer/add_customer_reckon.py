import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon,update_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_reckon_customer(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_customer")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        sage_customer = dbname['sage_customer']

        x = sage_customer.find({"job_id": job_id,"is_pushed":0})
        sage_customer1 = []
        for k in x:
            sage_customer1.append(k)

        for i in range(0, len(sage_customer1)):
            _id = sage_customer1[i]["_id"]
            QuerySet1 = {"Addresses": []}
            if "Name" in sage_customer1[i]:
                QuerySet1["FirstNameBranchName"] = sage_customer1[i].get(
                    "Name", None)
            
                QuerySet1["SurnameBusinessName"] = sage_customer1[i].get(
                    "Name", None)
                QuerySet1["Description"] = sage_customer1[i].get(
                    "Name", None)
                QuerySet1["Branch"] = None
                QuerySet1["Notes"] = None

            Addresses1 = {}

            if "PostalAddress01" in  sage_customer1[i]:
                Addresses1["Line1"] = sage_customer1[i].get(
                    "PostalAddress01", None)

            if "PostalAddress02" in sage_customer1[i]:
                Addresses1["Suburb"] = sage_customer1[i].get(
                    "PostalAddress02", None)
                
            if "PostalAddress04" in sage_customer1[i]:
               
                Addresses1["State"] = sage_customer1[i].get(
                    "PostalAddress04", None)
            if "PostalAddress05" in sage_customer1[i]:
                postaldata=sage_customer1[i]["PostalAddress05"]
                data_type=type(postaldata)

                if data_type==int:
                    if sage_customer1[i]["PostalAddress05"] > 3 and  sage_customer1[i]["PostalAddress05"]< 5:
                        Addresses1["Postcode"] = sage_customer1[i].get(
                            "PostalAddress05", None)
                else:
                    Addresses1["Postcode"] = ""
                    
                Addresses1["Country"] = sage_customer1[i].get(
                    "PostalAddress05", None)
            Addresses1["AddressType"] = "Postal"
            QuerySet1["Addresses"].append(Addresses1)

            Addresses2 = {} 
            if "DeliveryAddress01" in sage_customer1[i]:
                Addresses2["Line1"] = sage_customer1[i].get(
                    "DeliveryAddress01", None)
            if "DeliveryAddress02" in sage_customer1[i]:
                Addresses2["Suburb"] = sage_customer1[i].get(
                    "DeliveryAddress02", None)
            if "DeliveryAddress04" in sage_customer1[i]:
                Addresses2["State"] = sage_customer1[i].get(
                    "DeliveryAddress04", None)
            if "DeliveryAddress05" in sage_customer1[i]:

                postaldata=sage_customer1[i]["DeliveryAddress05"]
                data_type=type(postaldata)

                if data_type==int:
                    if sage_customer1[i]["DeliveryAddress05"] > 3 and  sage_customer1[i]["DeliveryAddress05"]< 5:
                        Addresses1["Postcode"] = sage_customer1[i].get(
                            "DeliveryAddress05", None)
                else:
                    Addresses1["Postcode"] = ""
                
                Addresses2["Country"] = sage_customer1[i].get(
                    "DeliveryAddress05", None)
            Addresses2["AddressType"] = "Business"
            QuerySet1["Addresses"].append(Addresses2)
            if "Telephone" in sage_customer1[i]:
                QuerySet1["PhoneNumber"] = sage_customer1[i].get("Telephone", None)

            if "Mobile" in sage_customer1[i]:
                QuerySet1["MobileNumber"] = sage_customer1[i].get("Mobile", None)
            
            if "Fax" in sage_customer1[i]:
                QuerySet1["FaxNumber"] = sage_customer1[i].get("Fax", None)
            
            if "WebAddress" in sage_customer1[i]:
                QuerySet1["Website"] = sage_customer1[i].get("WebAddress", None)

            if "Email" in sage_customer1[i]:

                Email_data=sage_customer1[i].get("Email",None).split(";")[0]
                QuerySet1["Email"] = Email_data

            if "TaxReference" in sage_customer1[i]:
                Abn_data=sage_customer1[i].get("TaxReference",None)
                QuerySet1["BusinessNumber1"]=Abn_data

            QuerySet1["IsCustomer"] = True
            QuerySet1["IsActive"] = True

            payload = json.dumps(QuerySet1)

            asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer,
                        _id, job_id, task_id, sage_customer1[i]["Name"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)


def add_reckon_default_customer(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_customer")
        dbname = get_mongodb_database()


        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        url = f"{base_url}/contacts"
        
        sage_customer = dbname['sage_customer']
        default_customer="default_customer"
        _id="6605202c8f1970a792dfb1b2"


        QuerySet1={}
        QuerySet1["FirstNameBranchName"] = "No Name - C"
        QuerySet1["SurnameBusinessName"] = "No Name - C"
        QuerySet1["Description"] = "No Name - C"
        
        QuerySet1["IsCustomer"] = True
        QuerySet1["IsActive"] = True

        payload = json.dumps(QuerySet1)


        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer,
                        _id, job_id, task_id, default_customer))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)



def update_reckon_customer(job_id, task_id):
    logging = log_config(job_id)
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        reckon_comman_customer = dbname['reckon_comman_customer']

        x = reckon_comman_customer.find({"job_id": job_id})
        reckon_comman_customer1 = []
        for k in x:
            reckon_comman_customer1.append(k)

        for i in range(0,len(reckon_comman_customer1)):
            print(i)
            _id=reckon_comman_customer1[i]['_id']
            task_id=reckon_comman_customer1[i]['task_id']
            reckon_comman_customer1[i].pop("_id")
            reckon_comman_customer1[i].pop("job_id")
            reckon_comman_customer1[i].pop("task_id")
            reckon_comman_customer1[i].pop("is_pushed")
            reckon_comman_customer1[i].pop("error")
            reckon_comman_customer1[i].pop("table_name")
            # reckon_comman_customer1[i].pop("payload")
            payload = json.dumps(reckon_comman_customer1[i])
        

            asyncio.run(update_data_in_reckon(url, post_headers, payload, reckon_comman_customer,
                        _id, job_id, task_id, reckon_comman_customer1[i]["Description"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

def update_reckon_supplier(job_id, task_id):
    logging = log_config(job_id)
    try:
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        reckon_comman_supplier = dbname['reckon_comman_supplier']

        x = reckon_comman_supplier.find({"job_id": job_id})
        reckon_comman_supplier1 = []
        for k in x:
            reckon_comman_supplier1.append(k)

        for i in range(0,len(reckon_comman_supplier1)):
            print(i)
            _id=reckon_comman_supplier1[i]['_id']
            task_id=reckon_comman_supplier1[i]['task_id']
            reckon_comman_supplier1[i].pop("_id")
            reckon_comman_supplier1[i].pop("job_id")
            reckon_comman_supplier1[i].pop("task_id")
            reckon_comman_supplier1[i].pop("is_pushed")
            reckon_comman_supplier1[i].pop("table_name")
            reckon_comman_supplier1[i].pop("error")
            # reckon_comman_customer1[i].pop("payload")
            payload = json.dumps(reckon_comman_supplier1[i])
        

            asyncio.run(update_data_in_reckon(url, post_headers, payload, reckon_comman_supplier1,
                        _id, job_id, task_id, reckon_comman_supplier1[i]["Description"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)