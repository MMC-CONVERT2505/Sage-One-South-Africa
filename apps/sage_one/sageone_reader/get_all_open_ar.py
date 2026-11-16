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


def get_all_open_ar_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_open_ar")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_open_ar_data"]

        
        sage_customer_ageing_data = dbname['sage_customer_ageing']

        x = sage_customer_ageing_data.find({"job_id": job_id,"is_pushed":0})
        sage_customer_ageing1 = []
        for k in x:
            sage_customer_ageing1.append(k)

        
        documents_to_insert = []

        for sage_customer_ageing in sage_customer_ageing1:

            for line in sage_customer_ageing.get("AgeingTransactions", []):

                QuerySet1 = {
                    "Customer": sage_customer_ageing["Customer"]["Name"],
                    "Date": sage_customer_ageing.get("Date"),                
                    "Total": sage_customer_ageing.get("Total"),
                    "Line_DocumentHeaderId" :line.get("DocumentHeaderId"),
                    "Line_DocumentTypeId" :line.get("DocumentTypeId"),
                    "Line_DocumentNumber" :line.get("DocumentNumber"),
                    "Line_Reference" :line.get("Reference"),
                    "Line_DocumentType" :line.get("DocumentType"),
                    "Line_Comment" :line.get("Comment"),
                    "Line_Date" :line.get("Date"),
                    "Line_DueDate" :line.get("DueDate"),
                    "Line_Total" :line.get("Total"),
                    "job_id": job_id,
                    "task_id": task_id
                }

                documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_Open_AR_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
