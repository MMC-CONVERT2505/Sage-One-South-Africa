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


def get_all_bank_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside coa data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_bank_data"]

        
        sage_bank_data = dbname['sage_bank']

        x = sage_bank_data.find({"job_id": job_id,"is_pushed":0})
        sage_bank1 = []
        for k in x:
            sage_bank1.append(k)

        
        documents_to_insert = []

        for sage_bank in sage_bank1:
            
            QuerySet1 = {
                "Name": sage_bank.get("Name"),
                "BankName": sage_bank.get("BankName"),
                "AccountNumber": sage_bank.get("AccountNumber"),
                "BranchName": sage_bank.get("BranchName"),
                "BranchNumber": sage_bank.get("BranchNumber"),
                "PaymentMethod": sage_bank.get("PaymentMethod"),
                "Description": sage_bank.get("Description"),
                "DefaultPaymentMethodId": sage_bank.get("DefaultPaymentMethodId"),
                "ID": sage_bank.get("ID"),
                "job_id": job_id,
                "task_id": task_id
            }

            documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_bank_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
