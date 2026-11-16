"""
Allocation file in the QBO template.

1. Credit allocation (credit note -> invoice, vendor credit -> bill): in QBO this is a zero-amount
   payment with two LinkedTxn lines, so every allocation produces 2 rows,
   both with the same TXN number (SageOne allocation ID).
2. Payment allocation (receipt -> invoice, supplier payment -> bill): one receipt / payment = one QBO
   payment (TXN number = receipt / payment number). One row per invoice / bill it was applied to.
   Total amount = total of the receipt / payment, Bank = its SageOne bank account.
"""
import traceback
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config
from apps.sage_one.sageone_reader.get_all_invoice_allocation import to_ddmmyy

# side -> settings
QBO_SIDES = {
    "invoice": {
        "target": "alloc_invoice", "credit": "alloc_credit_note", "payment": "alloc_invoice_payment",
        "name_field": "CustomerName", "name_column": "Customer ref name",
        "target_type": "Invoice", "credit_type": "Credit Memo",
        "out": "sage_all_qbo_invoice_allocation_data",
    },
    "bill": {
        "target": "alloc_bill", "credit": "alloc_vendorcredit", "payment": "alloc_bill_payment",
        "name_field": "SupplierName", "name_column": "Vendor ref name",
        "target_type": "Bill", "credit_type": "Vendor Credit",
        "out": "sage_all_qbo_bill_allocation_data",
    },
}


def build_qbo_allocation(job_id, task_id, side):
    logging = log_config(job_id)
    s = QBO_SIDES[side]
    try:
        logging.info(f"{job_id} inside build_qbo_allocation {side}")
        dbname = get_mongodb_database()

        Collection = dbname[s["out"]]
        # Avoid duplicate rows on retry
        Collection.delete_many({"job_id": job_id})

        def by_id(collection_name):
            return {x["ID"]: x for x in dbname[collection_name].find({"job_id": job_id}, {"_id": 0, "job_id": 0})}

        targets, credits, payments = by_id(s["target"]), by_id(s["credit"]), by_id(s["payment"])
        banks = {b["ID"]: b.get("Name") for b in by_id("alloc_bank_account").values()}

        credit_rows = []
        payment_lines = {}  # payment ID -> [(allocation, target)]

        for sage_allocation in dbname["alloc_allocation"].find({"job_id": job_id}, {"_id": 0}):
            target = targets.get(sage_allocation.get("AllocatedToDocumentId"))
            if target is None:
                continue
            source_id = sage_allocation.get("SourceDocumentId")

            if source_id in credits:
                source = credits[source_id]
                header = {
                    "TXN number": str(sage_allocation.get("ID")),
                    s["name_column"]: target.get(s["name_field"]) or source.get(s["name_field"]),
                    "TXN date": to_ddmmyy(sage_allocation.get("Created")),
                    "Total amount": 0,
                    "Memo": f"{source.get('DocumentNumber')} applied to {target.get('DocumentNumber')}",
                }
                for doc, doc_type in ((target, s["target_type"]), (source, s["credit_type"])):
                    credit_rows.append({
                        **header,
                        "Voucher number": doc.get("DocumentNumber"),
                        "Voucher type": doc_type,
                        "LinkedTXN amount": sage_allocation.get("Total"),
                        "Bank": None,
                        "Reference No.": doc.get("Reference"),
                    })

            elif source_id in payments:
                payment_lines.setdefault(source_id, []).append((sage_allocation, target))

        payment_rows = []
        for payment_id, lines in payment_lines.items():
            payment = payments[payment_id]
            for sage_allocation, target in lines:
                payment_rows.append({
                    "TXN number": payment.get("DocumentNumber"),
                    s["name_column"]: target.get(s["name_field"]),
                    "TXN date": to_ddmmyy(payment.get("Date")),
                    "Total amount": payment.get("Total"),
                    "Memo": payment.get("Reference"),
                    "Voucher number": target.get("DocumentNumber"),
                    "Voucher type": s["target_type"],
                    "LinkedTXN amount": sage_allocation.get("Total"),
                    "Bank": banks.get(payment.get("BankAccountId")),
                    "Reference No.": target.get("Reference"),
                })

        documents_to_insert = [{**row, "job_id": job_id, "task_id": task_id} for row in credit_rows + payment_rows]
        for i in range(0, len(documents_to_insert), 5000):
            Collection.insert_many(documents_to_insert[i:i + 5000])
        logging.info(f"{len(documents_to_insert)} documents inserted into {s['out']} "
                     f"({len(credit_rows)} credit rows, {len(payment_rows)} payment rows)")
        return len(documents_to_insert)

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        raise


def get_all_qbo_invoice_allocation_data(job_id, task_id):
    return build_qbo_allocation(job_id, task_id, "invoice")


def get_all_qbo_bill_allocation_data(job_id, task_id):
    return build_qbo_allocation(job_id, task_id, "bill")
