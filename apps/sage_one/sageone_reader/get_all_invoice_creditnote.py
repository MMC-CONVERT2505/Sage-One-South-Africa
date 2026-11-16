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


def get_all_invoice_creditnote_data(job_id, task_id):
    logging =  log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_invoice")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_invoice_creditnote_data"]

        
        sage_credit_note_data = dbname['sage_credit_note']

        x = sage_credit_note_data.find({"job_id": job_id,"is_pushed":0})
        sage_credit_note1 = []
        for k in x:
            sage_credit_note1.append(k)

        documents_to_insert = []
        for sage_credit_note in sage_credit_note1:
            for line in sage_credit_note.get("Lines", []):
                QuerySet1 = {
                    
                    "CustomerName": sage_credit_note.get("CustomerName",None),
                    "DueDate": sage_credit_note.get("DueDate"),                
                    "CustomerId": sage_credit_note.get("CustomerId"),
                    "ID": sage_credit_note.get("ID"),
                    "Date": sage_credit_note.get("Date"),
                    "Inclusive": sage_credit_note.get("Inclusive"),
                    "DiscountPercentage": sage_credit_note.get("DiscountPercentage"),
                    "DocumentNumber": sage_credit_note.get("DocumentNumber"),
                    "Reference": sage_credit_note.get("Reference"),
                    "Message": sage_credit_note.get("Message"),
                    "Discount": sage_credit_note.get("Discount"),
                    "Exclusive": sage_credit_note.get("Exclusive"),
                    "Tax": sage_credit_note.get("Tax"),
                    "Total": sage_credit_note.get("Total"),
                    "AmountDue": sage_credit_note.get("AmountDue"),
                    "TaxPeriodId": sage_credit_note.get("TaxPeriodId"),
                    "Line_SelectionId" :line.get("SelectionId"),
                    "Line_TaxTypeId" :line.get("TaxTypeId"),
                    "LineType" :line.get("LineType"),
                    "Line_Description" :line.get("Description"),
                    "Line_Quantity" :line.get("Quantity"),
                    "Line_Exclusive" :line.get("Exclusive"),
                    "Line_Discount" :line.get("Discount"),
                    "Line_Id" :line.get("ID"),
                    "Line_DiscountPercentage" :line.get("DiscountPercentage"),
                    "Line_UnitPriceExclusive" :line.get("UnitPriceExclusive"),
                    "Line_UnitPriceInclusive" :line.get("UnitPriceInclusive"),
                    "Line_Comments" :line.get("Comments"),
                    "Line_Total" :line.get("Total"),
                    "Line_Tax" :line.get("Tax"),
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
