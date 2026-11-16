import traceback
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config


def to_ddmmyy(value):
    """'2016-11-23T00:00:00Z' -> '23/11/2016'"""
    if not value:
        return None
    return f"{value[8:10]}/{value[5:7]}/{value[0:4]}"


def get_all_invoice_allocation_data(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_all_invoice_allocation_data")
        dbname = get_mongodb_database()

        Collection = dbname["sage_all_invoice_allocation_data"]
        # Avoid duplicate rows on retry
        Collection.delete_many({"job_id": job_id})

        fields = {"_id": 0, "ID": 1, "DocumentNumber": 1, "Date": 1, "CustomerName": 1, "Reference": 1}
        sage_invoice = {i["ID"]: i for i in dbname["alloc_invoice"].find({"job_id": job_id}, fields)}
        # Only credit note -> invoice allocations (not receipts)
        sage_credit_note = {c["ID"]: c for c in dbname["alloc_credit_note"].find({"job_id": job_id}, fields)}

        documents_to_insert = []

        for sage_allocation in dbname["alloc_allocation"].find({"job_id": job_id}, {"_id": 0}):
            invoice = sage_invoice.get(sage_allocation.get("AllocatedToDocumentId"))
            credit_note = sage_credit_note.get(sage_allocation.get("SourceDocumentId"))
            if invoice is None or credit_note is None:
                continue

            QuerySet1 = {
                "Invoice Number": invoice.get("DocumentNumber"),
                "Credit Note Number": credit_note.get("DocumentNumber"),
                "Amount": sage_allocation.get("Total"),
                "Created Date": to_ddmmyy(sage_allocation.get("Created")),
                "Customer Name": invoice.get("CustomerName") or credit_note.get("CustomerName"),
                "Credit Note Date": to_ddmmyy(credit_note.get("Date")),
                "Invoice Date": to_ddmmyy(invoice.get("Date")),
                "Invoice Reference No.": invoice.get("Reference"),
                "Credit Note Reference No.": credit_note.get("Reference"),
                "job_id": job_id,
                "task_id": task_id,
            }
            documents_to_insert.append(QuerySet1)

        for i in range(0, len(documents_to_insert), 5000):
            Collection.insert_many(documents_to_insert[i:i + 5000])
        logging.info(f"{len(documents_to_insert)} documents inserted into sage_all_invoice_allocation_data")
        return len(documents_to_insert)

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        raise
