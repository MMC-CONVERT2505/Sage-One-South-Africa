"""
Fetcher that pulls the data needed for the Invoice / Bill allocation files from SageOne.

- SageOne returns at most 100 records per call, so it loops page by page (no recursion,
  so it does not crash even on 200,000+ records).
- Every page is saved to MongoDB as soon as it arrives (upsert on job_id + ID, so no duplicates).
- If the internet / SageOne goes down it waits and retries (5s, 10s, 20s ... 60s),
  and starts one page back once the connection returns.
- If the outage lasts too long it raises AllocationFetchError; pressing Start / Retry
  resumes from the data that has already been fetched.
"""
import os
import time

import requests
from pymongo import ASCENDING, UpdateOne

from apps.mmc_settings.all_settings import get_settings_sageone
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

BASE_URL = "https://accounting.sageone.co.za/api/2.0.0"
PAGE_SIZE = 100  # SageOne maximum
DELAY_BETWEEN_CALLS = float(os.getenv("ALLOCATION_DELAY_SECONDS", "1"))
MAX_WAIT_MINUTES = float(os.getenv("ALLOCATION_MAX_WAIT_MINUTES", "120"))
REQUEST_TIMEOUT = (15, 180)  # (connect, read) seconds
BACKOFF = [5, 10, 20, 40, 60]

# collection -> (SageOne endpoint, extra params, fields to keep)
SOURCES = {
    "alloc_allocation": ("Allocation", "", ["ID", "SourceDocumentId", "AllocatedToDocumentId", "Total", "Created"]),
    "alloc_invoice": ("TaxInvoice", "&includeDetail=false", ["ID", "DocumentNumber", "Date", "CustomerName", "Reference"]),
    "alloc_credit_note": ("CustomerReturn", "&includeDetail=false", ["ID", "DocumentNumber", "Date", "CustomerName", "Reference"]),
    "alloc_bill": ("SupplierInvoice", "&includeDetail=false", ["ID", "DocumentNumber", "Date", "SupplierName", "Reference"]),
    "alloc_vendorcredit": ("SupplierReturn", "&includeDetail=false", ["ID", "DocumentNumber", "Date", "SupplierName", "Reference"]),
    "alloc_invoice_payment": ("CustomerReceipt", "&includeDetail=false",
                              ["ID", "DocumentNumber", "Date", "Total", "Reference", "BankAccountId"]),
    "alloc_bill_payment": ("SupplierPayment", "&includeDetail=false",
                           ["ID", "DocumentNumber", "Date", "Total", "Reference", "BankAccountId"]),
    "alloc_bank_account": ("BankAccount", "", ["ID", "Name"]),
}

# Xero files: only credit note -> invoice / vendor credit -> bill.
# QBO files also include the allocations made by receipts / supplier payments.
SIDE_SOURCES = {
    "invoice": ["alloc_allocation", "alloc_invoice", "alloc_credit_note"],
    "bill": ["alloc_allocation", "alloc_bill", "alloc_vendorcredit"],
    "qbo invoice": ["alloc_allocation", "alloc_invoice", "alloc_credit_note", "alloc_invoice_payment", "alloc_bank_account"],
    "qbo bill": ["alloc_allocation", "alloc_bill", "alloc_vendorcredit", "alloc_bill_payment", "alloc_bank_account"],
}


LABELS = {
    "alloc_allocation": "Allocations",
    "alloc_invoice": "Invoices",
    "alloc_credit_note": "Credit notes",
    "alloc_invoice_payment": "Receipts",
    "alloc_bill": "Bills",
    "alloc_vendorcredit": "Vendor credits",
    "alloc_bill_payment": "Supplier payments",
    "alloc_bank_account": "Bank accounts",
}

# task function name -> (side, output collection)
FUNCTION_SIDES = {
    "All Invoice Allocation Data": ("invoice", "sage_all_invoice_allocation_data"),
    "All Bill Allocation Data": ("bill", "sage_all_bill_allocation_data"),
    "All QBO Invoice Allocation Data": ("qbo invoice", "sage_all_qbo_invoice_allocation_data"),
    "All QBO Bill Allocation Data": ("qbo bill", "sage_all_qbo_bill_allocation_data"),
}


class AllocationFetchError(Exception):
    pass


def _save_progress(dbname, job_id, collection_name, have, total, eta=None, done=False):
    """Saves the status after every page for the frontend progress bar."""
    dbname["alloc_progress"].update_one(
        {"job_id": job_id, "collection": collection_name},
        {"$set": {"have": have, "total": total, "eta_min": eta, "done": done, "updated": time.time()}},
        upsert=True)


def allocation_progress(job_id, functions):
    """Progress of a job's allocation tasks: fetched / total for every data type, and the row count of each built file."""
    dbname = get_mongodb_database()
    saved = {p["collection"]: p for p in dbname["alloc_progress"].find({"job_id": job_id}, {"_id": 0})}
    sources, files = [], []
    for function_name in functions:
        if function_name not in FUNCTION_SIDES:
            continue
        side, out_collection = FUNCTION_SIDES[function_name]
        for name in SIDE_SOURCES[side]:
            if name not in sources:
                sources.append(name)
        files.append({"name": function_name, "rows": dbname[out_collection].count_documents({"job_id": job_id})})

    files_built = bool(files) and all(f["rows"] for f in files)
    items = []
    for name in sources:
        have = dbname[name].count_documents({"job_id": job_id})
        # Older jobs from before progress tracking: if the files are built, the data was complete
        p = saved.get(name) or ({"total": have, "done": True} if have and files_built else {})
        items.append({
            "label": LABELS[name],
            "have": have,
            "total": p.get("total"),
            "eta_min": p.get("eta_min"),
            "done": p.get("done", False),
            "running": bool(p) and not p.get("done") and time.time() - p.get("updated", 0) < 300,
        })
    return {"sources": items, "files": files}


def _get_page(url, headers, payload, logging, label):
    """Fetches one page. Waits and retries on network error / timeout / 5xx / 429 / invalid JSON."""
    waited = 0
    attempt = 0
    while True:
        wait = None
        try:
            response = requests.request("GET", url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            if response.status_code in (200, 201):
                return response.json()
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 60
                logging.warning(f"{label}: SageOne rate limit (429), waiting {wait}s")
            elif response.status_code >= 500:
                logging.warning(f"{label}: SageOne server error {response.status_code}")
            else:
                # Errors like 400 / 401 / 403 will not be fixed by retrying
                raise AllocationFetchError(
                    f"{label}: SageOne returned HTTP {response.status_code}: {response.text[:300]}")
        except AllocationFetchError:
            raise
        except (requests.exceptions.RequestException, ValueError) as ex:
            logging.warning(f"{label}: network/response error: {type(ex).__name__}: {ex}")

        if wait is None:
            wait = BACKOFF[min(attempt, len(BACKOFF) - 1)]
        attempt += 1
        if waited + wait > MAX_WAIT_MINUTES * 60:
            raise AllocationFetchError(
                f"{label}: could not connect to SageOne for {int(waited / 60)} minutes. "
                f"Check the internet connection and press Start/Retry again; the data will resume where it stopped.")
        logging.info(f"{label}: retrying in {wait}s (attempt {attempt})")
        time.sleep(wait)
        waited += wait


def fetch_collection(job_id, collection_name):
    """Fetches all data of one type. Data already fetched is skipped. Returns: (rows, total)."""
    logging = log_config(job_id)
    endpoint, extra, fields = SOURCES[collection_name]
    dbname = get_mongodb_database()
    collection = dbname[collection_name]
    collection.create_index([("job_id", ASCENDING), ("ID", ASCENDING)], unique=True)

    payload, headers, api_key_data, company_id_data = get_settings_sageone(job_id)
    url_template = (f"{BASE_URL}/{endpoint}/Get?$top={PAGE_SIZE}&$skip={{}}&$orderby=ID{extra}"
                    f"&apikey={{{{{api_key_data}}}}}&CompanyId={company_id_data}")

    have = collection.count_documents({"job_id": job_id})
    # On resume, go back one page so no record in between is missed (upsert prevents duplicates)
    skip = max(0, have - PAGE_SIZE)
    # Old rows lack the new fields (Date / Name), so fetch again from the start
    if have and collection.count_documents({"job_id": job_id, "$or": [{f: {"$exists": False}} for f in fields]}):
        skip = 0
        logging.info(f"{job_id} {collection_name}: new fields missing, refetching from the start")
    elif have:
        logging.info(f"{job_id} {collection_name}: resuming, {have} already saved, starting from skip {skip}")

    started = time.time()
    fetched_now = 0
    total = None
    _save_progress(dbname, job_id, collection_name, have, None)
    while True:
        data = _get_page(url_template.format(skip), headers, payload, logging, f"{job_id} {collection_name}")
        total = data.get("TotalResults", total)
        items = data.get("Results") or []
        if not items:
            break

        ops = []
        for item in items:
            doc = {k: item.get(k) for k in fields}
            doc["job_id"] = job_id
            ops.append(UpdateOne({"job_id": job_id, "ID": doc["ID"]}, {"$set": doc}, upsert=True))
        collection.bulk_write(ops, ordered=False)

        skip += len(items)
        fetched_now += len(items)
        have = collection.count_documents({"job_id": job_id})
        if total:
            elapsed = time.time() - started
            rate = fetched_now / elapsed if elapsed else 0
            eta = int((total - skip) / rate / 60) if rate else 0
            logging.info(f"{job_id} {collection_name}: {have:,} / {total:,} "
                         f"({have * 100 // total}%) ETA ~{eta} min")
            _save_progress(dbname, job_id, collection_name, have, total, eta)
        if len(items) < PAGE_SIZE or (total is not None and skip >= total):
            break
        time.sleep(DELAY_BETWEEN_CALLS)

    have = collection.count_documents({"job_id": job_id})
    total = total or 0
    if have < total:
        raise AllocationFetchError(
            f"{job_id} {collection_name}: only {have} / {total} records were fetched. Press Start/Retry again.")
    logging.info(f"{job_id} {collection_name}: complete {have:,} / {total:,}")
    _save_progress(dbname, job_id, collection_name, have, total, 0, done=True)
    return have, total


def fetch_allocation_sources(job_id, side):
    """side = 'invoice' or 'bill'. Fetches all the data needed for the allocation file."""
    return {name: fetch_collection(job_id, name) for name in SIDE_SOURCES[side]}
