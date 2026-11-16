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


def get_all_bank_transfer_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_bank_transfer")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_bank_transfer_data"]

        sage_bank_transfer_data = dbname['sage_bank_transfer']

        x = sage_bank_transfer_data.find({"job_id": job_id,"is_pushed":0})
        sage_bank_transfer1 = []
        for k in x:
            sage_bank_transfer1.append(k)


        documents_to_insert = []
        for sage_bank_transfer in sage_bank_transfer1:
            
            QuerySet1 = {
                
                "ID": sage_bank_transfer.get("ID",None),
                "Description": sage_bank_transfer.get("Description"),                
                "SelectionId": sage_bank_transfer.get("SelectionId"),
                "Type": sage_bank_transfer.get("Type"),
                "TaxTypeId": sage_bank_transfer.get("TaxTypeId"),
                "TaxPeriodId": sage_bank_transfer.get("TaxPeriodId"),
                "Payee": sage_bank_transfer.get("Payee"),
                "BankAccountId": sage_bank_transfer.get("BankAccountId"),
                "Date": sage_bank_transfer.get("Date"),
                "Memo": sage_bank_transfer.get("Memo"),
                "Reference": sage_bank_transfer.get("Reference"),
                "Exclusive": sage_bank_transfer.get("Exclusive"),
                "Tax": sage_bank_transfer.get("Tax"),
                "Total": sage_bank_transfer.get("Total"), 
                "job_id": job_id,
                "task_id": task_id
            }

            documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_bank_transfer_data")
            
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
