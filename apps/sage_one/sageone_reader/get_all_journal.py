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


def get_all_journal_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside journal data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_journal_data"]

        
        sage_manual_journal_data = dbname['sage_manual_journal']

        x = sage_manual_journal_data.find({"job_id": job_id,"is_pushed":0})
        sage_manual_journal1 = []
        for k in x:
            sage_manual_journal1.append(k)

        
        documents_to_insert = []

        for sage_manual_journal in sage_manual_journal1:
            
            QuerySet1 = {
                
                "ID": sage_manual_journal.get("ID",None),
                "Date": sage_manual_journal.get("Date",None),
                "Effect": sage_manual_journal.get("Effect",None),
                "AccountId": sage_manual_journal.get("AccountId",None),
                "Reference": sage_manual_journal.get("Reference",None),
                "Description": sage_manual_journal.get("Description",None),
                "TaxTypeId": sage_manual_journal.get("TaxTypeId",None),
                "TaxPeriodId": sage_manual_journal.get("TaxPeriodId",None),
                "Exclusive": sage_manual_journal.get("Exclusive",None),
                "Tax": sage_manual_journal.get("Tax",None),
                "Total": sage_manual_journal.get("Total",None),
                "ContraAccountId": sage_manual_journal.get("ContraAccountId",None),
                "Memo": sage_manual_journal.get("Memo",None),
                "Debit": sage_manual_journal.get("Debit",None),
                "Credit": sage_manual_journal.get("Credit",None),   
 
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
