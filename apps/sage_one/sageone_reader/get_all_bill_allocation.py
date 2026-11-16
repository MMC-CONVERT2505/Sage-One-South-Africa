import traceback
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
from apps.sage_one.sageone_reader.get_all_invoice_allocation import to_ddmmyy


def get_all_bill_allocation_data(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_all_bill_allocation_data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_bill_allocation_data"]
        # Avoid duplicate rows on retry
        Collection.delete_many({"job_id": job_id})

        fields = {"_id": 0, "ID": 1, "DocumentNumber": 1, "Date": 1, "SupplierName": 1, "Reference": 1}
        sage_bill = {b["ID"]: b for b in dbname["alloc_bill"].find({"job_id": job_id}, fields)}
        # Only vendor credit -> bill allocations (not supplier payments)
        sage_vendor_credit = {v["ID"]: v for v in dbname["alloc_vendorcredit"].find({"job_id": job_id}, fields)}

        documents_to_insert = []

        for sage_allocation in dbname["alloc_allocation"].find({"job_id": job_id}, {"_id": 0}):
            bill = sage_bill.get(sage_allocation.get("AllocatedToDocumentId"))
            vendor_credit = sage_vendor_credit.get(sage_allocation.get("SourceDocumentId"))
            if bill is None or vendor_credit is None:
                continue

            QuerySet1 = {
                "Invoice Number": bill.get("DocumentNumber"),
                "Credit Note Number": vendor_credit.get("DocumentNumber"),
                "Amount": sage_allocation.get("Total"),
                "Created Date": to_ddmmyy(sage_allocation.get("Created")),
                "Vendor Name": bill.get("SupplierName") or vendor_credit.get("SupplierName"),
                "Bill Credit Date": to_ddmmyy(vendor_credit.get("Date")),
                "Bill Date": to_ddmmyy(bill.get("Date")),
                "Bill Reference No.": bill.get("Reference"),
                "Bill Credit Reference No.": vendor_credit.get("Reference"),
                "job_id": job_id,
                "task_id": task_id,
            }
            documents_to_insert.append(QuerySet1)

        for i in range(0, len(documents_to_insert), 5000):
            Collection.insert_many(documents_to_insert[i:i + 5000])
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_bill_allocation_data")
        return len(documents_to_insert)

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        raise
