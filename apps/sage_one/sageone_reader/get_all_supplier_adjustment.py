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


def get_all_supplier_adjustment_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_supplier_adjustment")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_supplier_adjustment_data"]

        
        sage_supplier_adjustment_data = dbname['sage_supplier_adjustment']

        x = sage_supplier_adjustment_data.find({"job_id": job_id,"is_pushed":0})
        sage_supplier_adjustment1 = []
        for k in x:
            sage_supplier_adjustment1.append(k)

        
        documents_to_insert = []

        for sage_supplier_adjustment in sage_supplier_adjustment1:
            credit_data=None
            debit_data=None
            if sage_supplier_adjustment.get("Total") > 0:
                credit_data=sage_supplier_adjustment.get("Total")
            else:
                debit_data=0

            QuerySet1 = {
                "ID": sage_supplier_adjustment.get("ID",None),
                "Date": sage_supplier_adjustment.get("Date"),                
                "SupplierId": sage_supplier_adjustment.get("SupplierId"),
                "DocumentNumber": sage_supplier_adjustment.get("DocumentNumber"),
                "Reference": sage_supplier_adjustment.get("Reference"),
                "Description": sage_supplier_adjustment.get("Description"),
                "TaxTypeId": sage_supplier_adjustment.get("TaxTypeId"),
                "Exclusive": sage_supplier_adjustment.get("Exclusive"),
                "Tax": sage_supplier_adjustment.get("Tax"),
                "ContraAccountId": sage_supplier_adjustment.get("ContraAccountId"),
                "Total": sage_supplier_adjustment.get("Total"),
                "Credit":credit_data,
                "Debit" : debit_data,
                "job_id": job_id,
                "task_id": task_id
            }
            documents_to_insert.append(QuerySet1)
        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_supplier_adjustment_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
