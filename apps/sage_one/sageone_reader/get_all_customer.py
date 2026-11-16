import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config
from apps.home.data_util import get_job_details


def get_all_customer_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside coa data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_customer_data"]

        
        sage_customer_data = dbname['sage_customer']

        x = sage_customer_data.find({"job_id": job_id,"is_pushed":0})
        sage_customer1 = []
        for k in x:
            sage_customer1.append(k)

        
        documents_to_insert = []

        for sage_customer in sage_customer1:
            
            QuerySet1 = {
                
                "Name": sage_customer.get("Name",None),
                "TaxReference": sage_customer.get("TaxReference",None),
                "ContactName": sage_customer.get("ContactName",None),
                "Telephone": sage_customer.get("Telephone",None),
                "Fax": sage_customer.get("Fax",None),
                "Mobile": sage_customer.get("Mobile",None),
                "Email": sage_customer.get("Email",None),
                "WebAddress": sage_customer.get("WebAddress",None),
                "PostalAddress01": sage_customer.get("PostalAddress01",None),
                "PostalAddress02": sage_customer.get("PostalAddress02",None),
                "PostalAddress03": sage_customer.get("PostalAddress03",None),
                "PostalAddress04": sage_customer.get("PostalAddress04",None),
                "PostalAddress05": sage_customer.get("PostalAddress05",None),
                "DeliveryAddress01": sage_customer.get("DeliveryAddress01",None),
                "DeliveryAddress02": sage_customer.get("DeliveryAddress02",None),
                "DeliveryAddress03": sage_customer.get("DeliveryAddress03",None),
                "DeliveryAddress04": sage_customer.get("DeliveryAddress04",None),
                "DeliveryAddress05": sage_customer.get("DeliveryAddress05",None),
                "ID": sage_customer.get("ID",None),
                "job_id": job_id,
                "task_id": task_id
            }

            documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_invoice_payment_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
