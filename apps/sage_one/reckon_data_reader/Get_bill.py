import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_reckon_bill(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside get_reckon_bill-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        collection = dbname["reckon_bill"]
        # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
        url = f"{base_url}/bills/120000"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        logging.info(f"{job_id} get_reckon_bill--> url -->{url} response status-->{response.status_code}")
        arr = []
        for item in JsonResponse:

            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_bill"
            item['error'] = None
            item["is_pushed"] = 0
            arr.append(item)
                
         

            # Move the following line inside the loop
        collection.insert_many(arr)
        logging.info(f"{job_id} inserted_many data in reckon_bill")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

# The rest of your code...


def get_reckon_bill_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd

    print("get reckon bill")

    logging = log_config(job_id)

    try:
        logging.info(f"{job_id} inside get_reckon_bill_excel-------------updated")

        # MongoDB setup
        dbname = get_mongodb_database()
        collection = dbname["reckon_bill_excel"]

        # Get Reckon settings
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/bills/100000"
        logging.info(f"{job_id} - API Request URL: {url}")

        # API request
        response = requests.get(url, headers=get_headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        bills = json_data.get("Items",[])  # Adjust key if needed


        arr = []
        for item in bills:
            bill_id = item.get("BillID")
            if not bill_id:
                logging.warning(f"{job_id} - Skipping bill without ID")
                continue

            # Get full bill details with line items
            detail_url = f"{base_url}/bills/{bill_id}"
            try:
                detail_response = requests.get(detail_url, headers=get_headers, timeout=5)
                detail_response.raise_for_status()
                bill_detail = detail_response.json()

            except Exception as e:
                logging.error(f"{job_id} - Failed to get bill detail for {bill_id}: {e}")
                continue

            line_items = bill_detail.get("LineItems", [])
            amounttx = "TaxInclusive" if item.get("AmountTaxStatus") in [3, "3"] else "TaxExclusive"
        
            for line in line_items:
                record = {
                    "BillID": bill_id,
                    "BillNumber": item.get("BillNumber"),
                    "CustomerID": item.get("CustomerID"),
                    "CustomerName": item.get("CustomerName"),
                    "BillDate": item.get("BillDate"),
                    "DueDate": item.get("DueDate"),
                    "TotalAmount": item.get("BillAmount"),
                    "Balance": item.get("Balance"),
                    "Status": item.get("Status"),
                    "TaxAmount": item.get("BillTax"),
                    "Reference":item.get("Reference"),
                    "AmountTaxStatus": amounttx,
                    "Notes":item.get("Notes"),
                    
                    # Line item details
                    "LineID": line.get("Id"),
                    "AccountingCategoryId": line.get("AccountingCategoryId"),
                    "ChargeableItemId": line.get("ChargeableItemId"),
                    "LineNo": line.get("LineNo"),
                    "LineDescription": line.get("Description"),
                    "LineQuantity": line.get("Quantity"),
                    "LineProjectId": line.get("ProjectId"),
                    "LineUnitPriceExTax": line.get("UnitPriceExTax"),
                    "LineUnitPriceTax": line.get("UnitPriceTax"),
                    "LineUnitPricePrecision": line.get("UnitPricePrecision"),
                    "LineTaxGroupId": line.get("TaxGroupId"), 
                    "LineTaxIsModified": line.get("TaxIsModified"),
                    "LineTaxAmount": line.get("TaxAmount"),
                    "LineAmount": line.get("Amount"),
                    "Line_AccountId":line.get("AccountId"),
                    "job_id": job_id,
                    "task_id": task_id,
                }
                arr.append(record)

        if arr:
            print("stored bill data ")
            # Save to MongoDB
            collection.insert_many(arr)
            logging.info(f"{job_id} - Inserted {len(arr)} records into reckon_bill")

            # Save to Excel
            # df = pd.DataFrame(arr)
            # excel_file = f"/home/dinesh/Downloads/reckon_bill_{job_id}.xlsx"
            # df.to_excel(excel_file, index=False)
            # logging.info(f"{job_id} - Data saved to Excel: {excel_file}")
            # print(f"{job_id} - Data saved to Excel: {excel_file}")
        else:
            logging.warning(f"{job_id} - No bill data found to insert")

    except Exception as ex:
        print(ex,"ex")
        traceback.print_exc()
        logging.error(f"{job_id} - Error in get_reckon_bill_excel: {ex}", exc_info=True)



def get_reckon_bill_vendorcredit_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd

    print("get reckon get_reckon_bill_vendorcredit_excel")

    logging = log_config(job_id)

    try:
        logging.info(f"{job_id} inside get_reckon_bill_vendorcredit_excel-------------updated")

        # MongoDB setup
        dbname = get_mongodb_database()
        collection = dbname["reckon_bill_vendorcredit_excel"]

        # Get Reckon settings
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/suppliercreditnotes/100000"
        logging.info(f"{job_id} - API Request URL: {url}")

        # API request
        response = requests.get(url, headers=get_headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        print(json_data,"json_data")
        bills = json_data.get("Items",[])  # Adjust key if needed

        print(bills,"billsbillsbillsbills")


        arr = []
        for item in bills:
            bill_id = item.get("Id")
            if not bill_id:
                logging.warning(f"{job_id} - Skipping bill without ID")
                continue

            # Get full bill details with line items
            detail_url = f"{base_url}/suppliercreditnotes/{bill_id}"
            try:
                detail_response = requests.get(detail_url, headers=get_headers, timeout=10)
                detail_response.raise_for_status()
                bill_detail = detail_response.json()

                print(bill_detail,"bill_detail")
            except Exception as e:
                logging.error(f"{job_id} - Failed to get bill detail for {bill_id}: {e}")
                continue

            line_items = bill_detail.get("LineItems", [])

            amounttx = "TaxInclusive" if item.get("AmountTaxStatus") in [3, "3"] else "TaxExclusive"

            for line in line_items:
                record = {
                    "BillID": bill_id,
                    "BillNumber": item.get("BillNumber"),
                    "SupplierId": item.get("SupplierId"),
                    "SupplierName": item.get("SupplierName"),
                    "BillDate": item.get("BillDate"),
              
                    "TotalAmount": item.get("BillAmount"),
                    "Balance": item.get("Balance"),
                    "Status": item.get("Status"),
                    "TaxAmount": item.get("Tax"),
                    "Reference":item.get("Reference"),
                    "AmountTaxStatus": amounttx,
                    "Notes":item.get("Notes"),
                    
                    # Line item details
                    "LineID": line.get("Id"),
                    "AccountingCategoryId": line.get("AccountingCategoryId"),
                    "ChargeableItemId": line.get("ChargeableItemId"),
                    "LineNo": line.get("LineNo"),
                    "LineDescription": line.get("Description"),
                    "LineQuantity": line.get("Quantity"),
                    "LineProjectId": line.get("ProjectId"),
                    "LineUnitPriceExTax": line.get("UnitPriceExTax"),
                    "LineUnitPriceTax": line.get("UnitPriceTax"),
                    "LineUnitPricePrecision": line.get("UnitPricePrecision"),
                    "LineTaxGroupId": line.get("TaxGroupId"),
                    "LineTaxIsModified": line.get("TaxIsModified"),
                    "LineTaxAmount": line.get("TaxAmount"),
                    "LineAmount": line.get("Amount"),
                    "Line_AccountId":line.get("AccountId"),
                    "job_id": job_id,
                    "task_id": task_id,
                }
                arr.append(record)

        if arr:
            print(arr,"arr data")
            print("stored bill data ")
            # Save to MongoDB
            collection.insert_many(arr)
            logging.info(f"{job_id} - Inserted {len(arr)} records into reckon_bill")

            # Save to Excel
            # df = pd.DataFrame(arr)
            # excel_file = f"/home/dinesh/Downloads/reckon_bill_{job_id}.xlsx"
            # df.to_excel(excel_file, index=False)
            # logging.info(f"{job_id} - Data saved to Excel: {excel_file}")
            # print(f"{job_id} - Data saved to Excel: {excel_file}")
        else:
            logging.warning(f"{job_id} - No bill data found to insert")

    except Exception as ex:
        print(ex,"ex")
        traceback.print_exc()
        logging.error(f"{job_id} - Error in get_reckon_bill_excel: {ex}", exc_info=True)




def get_reckon_bill_payment_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd


    try:
        print(f"{job_id} - Inside get_reckon_bill_payment_excel")

        # Fetch settings
        settings = get_settings_reckon(job_id)
        if not settings:
            print(f"{job_id} - Failed to retrieve API settings")
            return
        payload, base_url, headers, book, post_headers, get_headers = settings

        # Validate base_url and headers
        if not base_url:
            print(f"{job_id} - Base URL is None. Check get_settings_reckon.")
            return
        if not isinstance(get_headers, dict):
            print(f"{job_id} - Headers are incorrectly formatted: {get_headers}")
            return

        # MongoDB connection
        dbname = get_mongodb_database()
        collection = dbname["reckon_bill_payment_excel"]

        url = f"{base_url}/payments/10"


        print(f"{job_id} - API Request URL: {url}")

        try:
            response = requests.get(url, headers=get_headers, data=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"{job_id} - API request failed: {e}")
            return

        json_data = response.json()

        print(json_data,"json_data")
        print(f"{job_id} - JSON response received")


        # JsonResponse = json_data


        JsonResponse = json_data.get("Items", []) if isinstance(json_data, dict) else json_data

        if not isinstance(JsonResponse, list):
            print(f"{job_id} - Unexpected response format: {type(json_data)}")
            return

        if not JsonResponse:
            print(f"{job_id} - No invoices found in API response.")
            return

        arr = []

        print(JsonResponse,"JsonResponse")

        print(len(JsonResponse),"jsonResponse data ")
        for item in JsonResponse:
            invoice_id = item.get("Id")
            if not invoice_id:
                print(f"{job_id} - Skipping invoice with missing ID")
                continue

            # Fetch detailed invoice with line items
            detail_url = f"{base_url}/payments/{invoice_id}"
            print(f"{job_id} - Detail API URL: {detail_url}")
            try:
                detail_resp = requests.get(detail_url, headers=get_headers, timeout=10)
                detail_resp.raise_for_status()
                detail_data = detail_resp.json()

                print(detail_data,"detail_data------")

            except Exception as e:
                print(f"{job_id} - Failed to fetch invoice detail for {invoice_id}: {e}")
                continue

            line_items = detail_data.get("AllocationSplit", [])
            if not line_items:
                print(f"{job_id} - No line items found for invoice {invoice_id}")
                continue

            for line in line_items:
                print(f"{job_id} - Processing line item for invoice {invoice_id}")

                QuerySet1 = {
                    "pmt_id": item.get("Id"),
                    "CashbookID": item.get("CashbookID"),
                    "BankAccountId":item.get("BankAccountId"),

                    "ContactId": item.get("ContactId"),
                    "Amount": item.get("Amount"),
                    "AllocateFullAmount": item.get("AllocateFullAmount"),
                    "PaymentMethodId": item.get("PaymentMethodId"),
                    "Details": item.get("Details"),
                    "Reference": item.get("Reference"),
                    "ReconciliationStatus": item.get("ReconciliationStatus"),
                    "ContactName": item.get("ContactName"),
                    
                    # Line item fields
                    "Line_Id": line.get("Id"),
                    "Line_Inv_Id": line.get("InvoiceId"),
                    "Lineitem_Description": line.get("Description"),
                    "Line_ChargeableItemId":line.get("ChargeableItemId"),
                    "Lineitem_Quantity": line.get("Quantity"),
                    "Lineitem_UnitPriceExTax": line.get("UnitPriceExTax"),
                    "Lineitem_UnitPriceTax": line.get("UnitPriceTax"),
                    "Lineitem_TaxGroupId": line.get("TaxGroupId"),
                    "Lineitem_TaxAmount": line.get("TaxAmount"),
                    "Lineitem_AmountExTax": line.get("AmountExTax"),
                    "Lineitem_Amount": line.get("Amount"),


                    "Line_AccountId":line.get("AccountId"),
                    "job_id": job_id,

                }
                arr.append(QuerySet1)

        print(f"{job_id} - Total line item records collected: {len(arr)}")

        # Insert into MongoDB
        if arr:
            collection.insert_many(arr)
            print(f"{job_id} - Inserted {len(arr)} records into reckon_invoice")

            # Save to Excel
            # df = pd.DataFrame(arr)
            # # excel_file = f"/home/dinesh/Documents/reckon_invoice11_{job_id}.xlsx"
            # excel_file = f"/home/dinesh/Downloads/reckon_invoice11_{job_id}.xlsx"
            # df.to_excel(excel_file, index=False)
            # print(f"{job_id} - Data saved to Excel: {excel_file}")
        else:
            print(f"{job_id} - No data to insert")

    except Exception as ex:
        print(f"{job_id} - Unexpected error: {ex}")
        traceback.print_exc()
