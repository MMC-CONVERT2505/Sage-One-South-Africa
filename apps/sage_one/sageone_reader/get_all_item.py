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


def get_all_item_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside item data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_item_data"]

        
        sage_item_data = dbname['sage_item']

        x = sage_item_data.find({"job_id": job_id,"is_pushed":0})
        sage_item1 = []
        for k in x:
            sage_item1.append(k)

        
        documents_to_insert = []

        for sage_item in sage_item1:
            
            QuerySet1 = {
                
                "Description": sage_item.get("Description",None),
                "Code": sage_item.get("Code",None),
                "Physical": sage_item.get("Physical",None),
                "TaxTypeIdSales": sage_item.get("TaxTypeIdSales",None),
                "TaxTypeIdPurchases": sage_item.get("TaxTypeIdPurchases",None),
                "QuantityOnHand": sage_item.get("QuantityOnHand",None),
                "AverageCost": sage_item.get("AverageCost",None),
                "PriceInclusive": sage_item.get("PriceInclusive",None),
                "PriceExclusive": sage_item.get("PriceExclusive",None),
                "ID": sage_item.get("ID",None),
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
