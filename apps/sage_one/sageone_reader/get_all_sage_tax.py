import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config


def get_all_tax_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside item data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_tax_data"]

        
        sage_tax_data = dbname['sage_tax']

        x = sage_tax_data.find({"job_id": job_id,"is_pushed":0})
        sage_tax1 = []
        for k in x:
            sage_tax1.append(k)

        
        documents_to_insert = []

        for sage_tax in sage_tax1:
            
            QuerySet1 = {
                
                "Name": sage_tax.get("Name",None),
                "IsDefault": sage_tax.get("IsDefault",None),
                "HasActivity": sage_tax.get("HasActivity",None),
                "Active": sage_tax.get("Active",None),
                "TaxTypeDefaultUID": sage_tax.get("TaxTypeDefaultUID",None),
                "CompanyId": sage_tax.get("CompanyId",None),
                "ID": sage_tax.get("ID",None),
                "job_id": job_id,
                "task_id": task_id
            }
            documents_to_insert.append(QuerySet1)

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
            
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_tax_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
