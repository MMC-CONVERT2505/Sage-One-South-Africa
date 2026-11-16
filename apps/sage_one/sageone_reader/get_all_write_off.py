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


def get_all_customer_write_off_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_write_off")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_customer_write_off_data"]

        
        sage_customer_write_off_data = dbname['sage_customer_write_off']

        x = sage_customer_write_off_data.find({"job_id": job_id,"is_pushed":0})
        sage_customer_write_off1 = []
        for k in x:
            sage_customer_write_off1.append(k)

        
        documents_to_insert = []

        for sage_customer_write_off in sage_customer_write_off1:

            credit_data=None
            debit_data=None
            if sage_customer_write_off.get("Total") > 0:
                credit_data=sage_customer_write_off.get("Total")
            else:
                debit_data=0

            
            QuerySet1 = {
                "ID": sage_customer_write_off.get("ID",None),
                "Date": sage_customer_write_off.get("Date"),                
                "CustomerId": sage_customer_write_off.get("CustomerId"),
                "DocumentNumber": sage_customer_write_off.get("DocumentNumber"),
                "Reference": sage_customer_write_off.get("Reference"),
                "Description": sage_customer_write_off.get("Description"),
                "Comments": sage_customer_write_off.get("Comments"),
                "Total": sage_customer_write_off.get("Total"),
                "Credit":credit_data,
                "Debit" : debit_data,
                "job_id": job_id,
                "task_id": task_id
            }
            documents_to_insert.append(QuerySet1)
        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_customer_write_off_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
