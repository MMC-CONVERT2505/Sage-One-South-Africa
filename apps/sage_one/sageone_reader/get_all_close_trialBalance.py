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


def get_all_close_trial_balance_data(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_open_trial_balance")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_close_trial_balance_data"]

        
        sage_close_trial_balance_data = dbname['sage_close_trial_balance']

        x = sage_close_trial_balance_data.find({"job_id": job_id,"is_pushed":0})
        sage_close_trial_balance1 = []
        for k in x:
            sage_close_trial_balance1.append(k)

        
        documents_to_insert = []

        for sage_close_trial_balance in sage_close_trial_balance1:

            
            QuerySet1 = {
                "Name": sage_close_trial_balance.get("Name"),                
                "AccountNumber": sage_close_trial_balance.get("AccountNumber"),
                "Date": sage_close_trial_balance.get("Date"),                
                "Debit": sage_close_trial_balance.get("Debit"),
                "Credit": sage_close_trial_balance.get("Credit"),                
                "AccountTypeId": sage_close_trial_balance.get("AccountTypeId"),
                "AccountId": sage_close_trial_balance.get("AccountId"),                
                "job_id": job_id,
                "task_id": task_id
            }

            documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_Open_trial_balance_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
