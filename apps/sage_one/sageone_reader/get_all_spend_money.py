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


def get_all_spend_moeny_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_invoice_payment")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_spend_money_data"]

        
        sage_spend_money_data = dbname['sage_spend_money']

        x = sage_spend_money_data.find({"job_id": job_id,"is_pushed":0})
        sage_spend_money1 = []
        for k in x:
            sage_spend_money1.append(k)

        
        documents_to_insert = []

        for sage_spend_money in sage_spend_money1:
            
            QuerySet1 = {
                
                "ID": sage_spend_money.get("ID"),
                "AccountId": sage_spend_money.get("AccountId"),                
                "Date": sage_spend_money.get("Date"),
                "Payee": sage_spend_money.get("Payee"),
                "Description": sage_spend_money.get("Description"),
                "Reference": sage_spend_money.get("Reference"),
                "TaxTypeId": sage_spend_money.get("TaxTypeId"),
                "Comments": sage_spend_money.get("Comments"),
                "Exclusive": sage_spend_money.get("Exclusive"),
                "Tax": sage_spend_money.get("Tax"),
                "Total": sage_spend_money.get("Total"),
                "Reconciled": sage_spend_money.get("Reconciled"),
                "BankAccountId": sage_spend_money.get("BankAccountId"),
                "Accepted": sage_spend_money.get("Accepted"),
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
