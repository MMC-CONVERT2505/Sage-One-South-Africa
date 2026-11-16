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


def get_all_invoice_payment_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_invoice_payment")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_invoice_payment_data"]

        
        sage_invoice_paymnet = dbname['sage_invoice_payment']

        x = sage_invoice_paymnet.find({"job_id": job_id,"is_pushed":0})
        sage_invoice_payment1 = []
        for k in x:
            sage_invoice_payment1.append(k)

        sage_invoice = dbname["sage_invoice"].find({"job_id": job_id})
        sage_invoice1 = []
        for c6 in sage_invoice:
            sage_invoice1.append(c6)

        sage_allocation_data = dbname["sage_allocation"].find({"job_id": job_id})
        sage_allocation1 = []
        for c4 in sage_allocation_data:
            sage_allocation1.append(c4)

        documents_to_insert = []

        for sage_allocation in sage_allocation1:
            invoice_data = dbname["sage_invoice_payment"].find_one({"job_id": job_id, "ID": sage_allocation["SourceDocumentId"]})

            if invoice_data:

                print(invoice_data,"invoice_data")
                invoice1 = dbname["sage_invoice"].find_one({"job_id": job_id, "ID": sage_allocation["AllocatedToDocumentId"]})
                QuerySet1 = {
                    
                    "AID": sage_allocation.get("AllocatedToDocumentId"),
                    "AppliedAmount": sage_allocation.get("Total"),
                    "Invoice_number": invoice1.get("DocumentNumber")if invoice1 is not None else None,
                    "ID": invoice_data.get("ID"),
                    "Date": invoice_data.get("Date"),
                    "Payee": invoice_data.get("Payee"),
                    "DocumentNo": invoice_data.get("DocumentNumber"),
                    "Reference": invoice_data.get("Reference"),
                    "Description": invoice_data.get("Description"),
                    "CustomerName": invoice_data["Customer"]["Name"],
                    "Total": invoice_data.get("Total"),
                    "Discount": invoice_data.get("Discount"),
                    "comments": invoice_data.get("Comments"),
                    "TotalUnallocated": invoice_data.get("TotalUnallocated"),
                    "BankAccountId": invoice_data.get("BankAccountId"),
                    "Reconciled": invoice_data.get("Reconciled"),
                    "PaymentMethod": invoice_data.get("PaymentMethod"),
                    "job_id": job_id,
                    "task_id": task_id
                }

                documents_to_insert.append(QuerySet1)
        print(documents_to_insert,"documents_to_insert")

        if documents_to_insert:
            Collection.insert_many(documents_to_insert)
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_invoice_payment_data")
              
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
