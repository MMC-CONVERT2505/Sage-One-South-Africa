import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_reckon_supplier(job_id, task_id):
    logging =log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_supplier")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/contacts"

        sage_supplier = dbname['sage_supplier']

        x = sage_supplier.find({"job_id": job_id,"is_pushed":0})
        sage_supplier1 = []
        for k in x:
            sage_supplier1.append(k)

        for i in range(0, len(sage_supplier1)):
            _id = sage_supplier1[i]["_id"]
            QuerySet1 = {"Addresses": []}
            if "Name" in sage_supplier1[i]:
                QuerySet1["FirstNameBranchName"] = sage_supplier1[i].get(
                    "Name", None)
                QuerySet1["SurnameBusinessName"] = sage_supplier1[i].get(
                    "Name", None)
                QuerySet1["Description"] = sage_supplier1[i].get(
                    "Name", None)
            if "Branch" in sage_supplier1[i]:
                QuerySet1["Branch"] = sage_supplier1[i].get(
                    "Branch", None)
            if "BusinessNumber1" in sage_supplier1[i]:  
                QuerySet1["BusinessNumber1"] = sage_supplier1[i].get(
                    "BusinessNumber1", None)
            if "Notes" in sage_supplier1[i]: 
                QuerySet1["Notes"] = sage_supplier1[i].get(
                    "Notes", None)

            Addresses1 = {}
            if "PostalAddress01" in sage_supplier1[i]: 
                Addresses1["Line1"] = sage_supplier1[i].get(
                    "PostalAddress01", None)
            if "PostalAddress02" in sage_supplier1[i]: 
                Addresses1["Suburb"] = sage_supplier1[i].get(
                    "PostalAddress02", None)
            if "PostalAddress03" in sage_supplier1[i]: 
                Addresses1["State"] = sage_supplier1[i].get(
                    "PostalAddress03", None)
                
            if "PostalAddress05" in sage_supplier1[i]:
                postaldata=sage_supplier1[i]["PostalAddress05"]
                data_type=type(postaldata)

                if data_type==int:
                    if sage_supplier1[i]["PostalAddress05"] > 3 and  sage_supplier1[i]["PostalAddress05"]< 5:
                        Addresses1["Postcode"] = sage_supplier1[i].get(
                            "PostalAddress05", None)
                else:
                    Addresses1["Postcode"] = ""
            
                
                Addresses1["Country"] = sage_supplier1[i].get(
                    "PostalAddress05", None)
                
            Addresses1["AddressType"] = "Postal"
            QuerySet1["Addresses"].append(Addresses1)

            Addresses2 = {}
            if "DeliveryAddress01" in sage_supplier1[i]:
                Addresses2["Line1"] = sage_supplier1[i].get(
                    "DeliveryAddress01", None)
            if "DeliveryAddress02" in sage_supplier1[i]:
              
                Addresses2["Suburb"] = sage_supplier1[i].get(
                    "DeliveryAddress02", None)
            if "DeliveryAddress03" in sage_supplier1[i]:
            
                Addresses2["State"] = sage_supplier1[i].get(
                    "DeliveryAddress03", None)
            if "DeliveryAddress05" in sage_supplier1[i]:
                postaldata=sage_supplier1[i]["DeliveryAddress05"]
                data_type=type(postaldata)
                
                if data_type==int:
                    if sage_supplier1[i]["DeliveryAddress05"] > 3 and  sage_supplier1[i]["DeliveryAddress05"]< 5:
                        Addresses1["Postcode"] = sage_supplier1[i].get(
                            "DeliveryAddress05", None)
                else:
                    Addresses1["Postcode"] = ""

                Addresses2["Country"] = sage_supplier1[i].get(
                    "DeliveryAddress05", None)
            Addresses2["AddressType"] = "Business"
            QuerySet1["Addresses"].append(Addresses2)
            if "Telephone" in sage_supplier1[i]:
                QuerySet1["PhoneNumber"] = sage_supplier1[i].get("Telephone", None)

            if "Mobile" in sage_supplier1[i]:

                QuerySet1["MobileNumber"] = sage_supplier1[i].get("Mobile", None)
            if "Fax" in sage_supplier1[i]:
 
                QuerySet1["FaxNumber"] = sage_supplier1[i].get("Fax", None)
            if "WebAddress" in sage_supplier1[i]:
                QuerySet1["Website"] = sage_supplier1[i].get("WebAddress", None)

            if "Email" in sage_supplier1[i]:
                email_data=sage_supplier1[i].get("Email", None).split(";")[0]
                QuerySet1["Email"] = email_data

            if "TaxReference" in sage_supplier1[i]:
                Abn_data=sage_supplier1[i].get("TaxReference",None)
                
                QuerySet1["BusinessNumber1"]= Abn_data

                
            QuerySet1["IsSupplier"] = True
            QuerySet1["IsActive"] = True

            payload = json.dumps(QuerySet1)
            asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier,
                        _id, job_id, task_id, sage_supplier1[i]["Name"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex,exc_info=True)



def add_reckon_default_supplier(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_supplier")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        
        url = f"{base_url}/contacts"
        sage_supplier = dbname['sage_supplier1']
        default_supplier="default_supplier"
        _id="660522cd4b9a3418e5854ddf"
        QuerySet1={}
        QuerySet1["FirstNameBranchName"] = "No Name - S"
        QuerySet1["SurnameBusinessName"] = "No Name - S"
        QuerySet1["Description"] = "No Name - S"
        
        QuerySet1["IsSupplier"] = True
        QuerySet1["IsActive"] = True

        payload = json.dumps(QuerySet1)

        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier,
                _id, job_id, task_id, default_supplier))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)