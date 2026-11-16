# import traceback
# import requests
# from apps.mmc_settings.all_settings import get_settings_reckon
# from apps.util.db_mongo import get_mongodb_database
# from apps.util.log_file import log_config



# def get_reckon_invoice(job_id, task_id):
#     logging = log_config(job_id)
#     try:
#         print(f"{job_id} inside get _reckon_invoice-------------updated")
#         dbname = get_mongodb_database()
#         payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
#             job_id)
#         collection = dbname["reckon_invoice"]
#         # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
#         url = f"{base_url}/invoices/100000"

#         response = requests.request("GET", url, headers=get_headers, data=payload)
#         print(f"{job_id} get_reckon_invoice--> url -->{url} response status -->{response.status_code}")
#         JsonResponse1 = response.json()
#         JsonResponse = JsonResponse1['Items'] 
#         arr = []
#         for item in JsonResponse:

#             item["job_id"] = job_id
#             item["task_id"] = task_id
#             item['table_name'] = "reckon_invoice"
#             item['error'] = None
#             item["is_pushed"] = 0
#             arr.append(item)
                
         

#             # Move the following line inside the loop
#         collection.insert_many(arr)
#         print(f"{job_id} inserted many data in reckon_invoice")


#     except Exception as ex:
#         traceback.print_exc()
#         print(ex, exc_info=True)


# # The rest of your code...


import traceback
import requests
import pandas as pd
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config



def get_reckon_invoice(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get _reckon_invoice-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        collection = dbname["reckon_invoice"]
        # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
        url = f"{base_url}/invoices/12000"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        logging.info(f"{job_id} get_reckon_invoice--> url -->{url} response status -->{response.status_code}")
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 
        arr = []
        for item in JsonResponse:

            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_invoice"
            item['error'] = None
            item["is_pushed"] = 0
            arr.append(item)
                
         

            # Move the following line inside the loop
        collection.insert_many(arr)
        logging.info(f"{job_id} inserted many data in reckon_invoice")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)



# def get_reckon_invoice(job_id, task_id):
#     logging = log_config(job_id)

#     try:
#         print(f"{job_id} - Inside get_reckon_invoice")

#         # Fetch settings
#         settings = get_settings_reckon(job_id)
#         if not settings:
#             print(f"{job_id} - Failed to retrieve API settings")
#             return
#         payload, base_url, headers, book, post_headers, get_headers = settings

#         # Validate base_url
#         if not base_url:
#             print(f"{job_id} - Base URL is None. Check get_settings_reckon.")
#             return
#         # Validate headers
#         if not isinstance(get_headers, dict):
#             print(f"{job_id} - Headers are incorrectly formatted: {get_headers}")
#             return
#         dbname = get_mongodb_database()
#         collection = dbname["reckon_invoice"]

#         url = f"{base_url}/invoices?page=1&perpage=10000"
#         print(f"{job_id} - API Request URL: {url}")

#         # Handle connection issues
#         try:
#             response = requests.get(url, headers=get_headers, data=payload, timeout=10)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             print(f"{job_id} - API request failed: {e}")
#             return
        
#         json_data = response.json()

#         print(json_data,"json data ")

#         if isinstance(json_data, dict):
#             JsonResponse = json_data.get("list", [])
#         elif isinstance(json_data, list):
#             JsonResponse = json_data
#         else:
#             print(f"{job_id} - Unexpected response format: {type(json_data)}")
#             return
        
#         # JsonResponse = json_data


#         arr = []
#         for item in JsonResponse:
#             invoice_id = item.get("Id")

#             # Fetch full invoice details to get lineItems
#             detail_url = f"{base_url}/invoices/{invoice_id}"
#             try:
#                 detail_resp = requests.get(detail_url, headers=get_headers, timeout=10)
#                 detail_resp.raise_for_status()
#                 detail_data = detail_resp.json()
#             except Exception as e:
#                 print(f"{job_id} - Failed to fetch invoice detail for {invoice_id}: {e}")
#                 continue

#             for line in detail_data.get("lineItems", []):
#                 QuerySet1 = {
#                     "Inv_id": item.get("Id"),
#                     "CashbookID": item.get("CashbookID"),
#                     "Inv_number": item.get("InvoiceNumber"),
#                     "CustomerID": item.get("CustomerID"),
#                     "CustomerName": item.get("CustomerName"),
#                     "InvoiceAmount": item.get("InvoiceAmount"),
#                     "InvoiceDate": item.get("InvoiceDate"),
#                     "DueDate": item.get("DueDate"),
#                     "Balance": item.get("Balance"),
#                     "Status": item.get("Status"),
#                     "Reference": item.get("Reference"),
#                     "Notes": item.get("Notes"),
#                     "IsOverdue": item.get("IsOverdue"),

#                     # Line item fields
#                     "Line_Id": line.get("lineId"),
#                     "Lineitemname": line.get("itemDetails", {}).get("item", {}).get("name"),
#                     "Lineitemprice": line.get("itemDetails", {}).get("price"),
#                     "Lineitemquantity": line.get("itemDetails", {}).get("quantity"),
#                     "LineitemdiscountAmount": line.get("itemDetails", {}).get("discountAmount"),
#                     "Line_Description": line.get("description"),
#                     "Line_taxid": line.get("taxRate", {}).get("id"),
#                     "Line_taxname": line.get("taxRate", {}).get("name"),
#                     "Line_taxAmount": line.get("taxAmount"),
#                     "Line_taxIsModified": line.get("taxIsModified"),

#                     "job_id": job_id,
#                     "task_id": task_id
#                 }
#                 arr.append(QuerySet1)
#         print(arr,"arr data ")

#         # Insert into MongoDB
#         if arr:
#             collection.insert_many(arr)
#             print(f"{job_id} - Inserted {len(arr)} records into reckon_invoice")

#             # Save to Excel
#             df = pd.DataFrame(arr)
#             excel_file = f"/home/dinesh/Documents/reckon_invoice11_{job_id}.xlsx"
#             df.to_excel(excel_file, index=False)
#             print(f"{job_id} - Data saved to Excel: {excel_file}")

#     except Exception as ex:
#         print("ex",ex)
#         print(f"{job_id} - Unexpected error: {ex}")
#         traceback.print_exc()


# def get_reckon_invoice(job_id, task_id):
#     logging = log_config(job_id)

#     try:
#         print(f"{job_id} - Inside get_reckon_invoice")

#         # Fetch settings
#         settings = get_settings_reckon(job_id)
#         if not settings:
#             print(f"{job_id} - Failed to retrieve API settings")
#             return
#         payload, base_url, headers, book, post_headers, get_headers = settings

#         # Validate base_url and headers
#         if not base_url:
#             print(f"{job_id} - Base URL is None. Check get_settings_reckon.")
#             return
#         if not isinstance(get_headers, dict):
#             print(f"{job_id} - Headers are incorrectly formatted: {get_headers}")
#             return

#         # MongoDB connection
#         dbname = get_mongodb_database()
#         collection = dbname["reckon_invoice"]

#         url = f"{base_url}/invoices?page=1&perpage=10000"
#         print(f"{job_id} - API Request URL: {url}")

#         try:
#             response = requests.get(url, headers=get_headers, data=payload, timeout=10)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             print(f"{job_id} - API request failed: {e}")
#             return

#         json_data = response.json()
#         print(json_data, "json data")

#         JsonResponse = json_data.get("list", []) if isinstance(json_data, dict) else json_data

#         if not isinstance(JsonResponse, list):
#             print(f"{job_id} - Unexpected response format: {type(json_data)}")
#             return

#         arr = []
#         for item in JsonResponse:
#             invoice_id = item.get("Id")
#             if not invoice_id:
#                 print(f"{job_id} - Skipping invoice with missing ID")
#                 continue

#             # Fetch detailed invoice with line items
#             detail_url = f"{base_url}/invoices/{invoice_id}"
#             print(detail_url,"detail_url")
#             try:
#                 detail_resp = requests.get(detail_url, headers=get_headers, timeout=10)
#                 detail_resp.raise_for_status()
#                 detail_data = detail_resp.json()

#                 print(detail_data,"detail_data------------")
#             except Exception as e:
#                 print(f"{job_id} - Failed to fetch invoice detail for {invoice_id}: {e}")
#                 continue
            
#             for line in detail_data.get("lineItems", []):
#                 print("line data")
#                 QuerySet1 = {
#                     "Inv_id": item.get("Id"),
#                     "CashbookID": item.get("CashbookID"),
#                     "Inv_number": item.get("InvoiceNumber"),
#                     "CustomerID": item.get("CustomerID"),
#                     "CustomerName": item.get("CustomerName"),
#                     "InvoiceAmount": item.get("InvoiceAmount"),
#                     "InvoiceDate": item.get("InvoiceDate"),
#                     "DueDate": item.get("DueDate"),
#                     "Balance": item.get("Balance"),
#                     "Status": item.get("Status"),
#                     "Reference": item.get("Reference"),
#                     "Notes": item.get("Notes"),
#                     "IsOverdue": item.get("IsOverdue"),

#                     # Line item fields
#                     "Line_Id": line.get("lineId"),
#                     "Lineitemname": line.get("itemDetails", {}).get("item", {}).get("name"),
#                     "Lineitemprice": line.get("itemDetails", {}).get("price"),
#                     "Lineitemquantity": line.get("itemDetails", {}).get("quantity"),
#                     "LineitemdiscountAmount": line.get("itemDetails", {}).get("discountAmount"),
#                     "Line_Description": line.get("description"),
#                     "Line_taxid": line.get("taxRate", {}).get("id"),
#                     "Line_taxname": line.get("taxRate", {}).get("name"),
#                     "Line_taxAmount": line.get("taxAmount"),
#                     "Line_taxIsModified": line.get("taxIsModified"),

#                     "job_id": job_id,
#                     "task_id": task_id
#                 }
#                 arr.append(QuerySet1)

#         print(f"{job_id} - Total line item records collected: {len(arr)}")

#         # Insert into MongoDB
#         if arr:
#             collection.insert_many(arr)
#             print(f"{job_id} - Inserted {len(arr)} records into reckon_invoice")

#             # Save to Excel
#             df = pd.DataFrame(arr)
#             excel_file = f"/home/dinesh/Documents/reckon_invoice11_{job_id}.xlsx"
#             df.to_excel(excel_file, index=False)
#             print(f"{job_id} - Data saved to Excel: {excel_file}")
#         else:
#             print(f"{job_id} - No data to insert")

#     except Exception as ex:
#         print(f"{job_id} - Unexpected error: {ex}")
#         traceback.print_exc()




##excel excution 


def get_reckon_invoice_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd


    try:
        print(f"{job_id} - Inside get_reckon_invoice_excel")

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
        collection = dbname["reckon_invoice_excel"]

        url = f"{base_url}/invoices/10000"


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
            detail_url = f"{base_url}/invoices/{invoice_id}"
            print(f"{job_id} - Detail API URL: {detail_url}")
            try:
                detail_resp = requests.get(detail_url, headers=get_headers, timeout=10)
                detail_resp.raise_for_status()
                detail_data = detail_resp.json()

                print(detail_data,"detail_data-----")

            except Exception as e:
                print(f"{job_id} - Failed to fetch invoice detail for {invoice_id}: {e}")
                continue

            line_items = detail_data.get("LineItems", [])
            if not line_items:
                print(f"{job_id} - No line items found for invoice {invoice_id}")
                continue

            amounttx = "TaxInclusive" if item.get("AmountTaxStatus") in [3, "3"] else "TaxExclusive"


            for line in line_items:
                print(f"{job_id} - Processing line item for invoice {invoice_id}")

                if "ChargeableItemId" in line and line["ChargeableItemId"] != None and line["ChargeableItemId"] != "00000000-0000-0000-0000-000000000000":

                    sales_account_id = dbname["reckon_item"].find_one({"job_id": job_id, "Id": line.get("ChargeableItemId")})
                    if sales_account_id:
                        sales_account_id = sales_account_id.get("SaleCategoryId")
                    else:

                        sales_account_id = None
                else:
                    sales_account_id = None
                QuerySet1 = {
                    "Inv_id": item.get("Id"),
                    "CashbookID": item.get("CashbookID"),
                    "Inv_number": item.get("InvoiceNumber"),
                    "CustomerID": item.get("CustomerID"),
                    "CustomerName": item.get("CustomerName"),
                    "InvoiceAmount": item.get("InvoiceAmount"),
                    "InvoiceDate": item.get("InvoiceDate"),
                    "DueDate": item.get("DueDate"),
                    "Balance": item.get("Balance"),
                    "Status": item.get("Status"),
                    "Reference": item.get("Reference"),
                    "Notes": item.get("Notes"),
                    "AmountTaxStatus": amounttx,
                    "IsOverdue": item.get("IsOverdue"),

                    # Line item fields
                    "Line_Id": line.get("Id"),
                    "Line_Inv_Id": line.get("InvoiceId"),
                    "Lineitem_Description": line.get("Description"),
                    "Line_ChargeableItemId":line.get("ChargeableItemId"),
                    "Lineitem_Quantity": line.get("Quantity"),
                    "LineProjectId": line.get("ProjectId",""),
                    "Lineitem_UnitPriceExTax": line.get("UnitPriceExTax"),
                    "Lineitem_UnitPriceTax": line.get("UnitPriceTax"),
                    "Lineitem_TaxGroupId": line.get("TaxGroupId"),
                    "Lineitem_TaxAmount": line.get("TaxAmount"),
                    "Lineitem_AmountExTax": line.get("AmountExTax"),
                    "Lineitem_Amount": line.get("Amount"),

                    "Line_accountId_data": line.get("AccountId"),

                    "Line_AccountId": (
                        sales_account_id.get("SaleCategoryId")
                        if isinstance(sales_account_id, dict) and sales_account_id.get("SaleCategoryId")
                        else None
                    ),
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




def get_reckon_invoice_creditnote_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd


    try:
        print(f"{job_id} - Inside get_reckon_invoice_creditnote_excel")

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
        collection = dbname["reckon_invoice_creditnote_excel"]

        url = f"{base_url}/creditnotes/10000"


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
            detail_url = f"{base_url}/creditnotes/{invoice_id}"
            print(f"{job_id} - Detail API URL: {detail_url}")
            try:
                detail_resp = requests.get(detail_url, headers=get_headers, timeout=10)
                detail_resp.raise_for_status()
                detail_data = detail_resp.json()

                print(detail_data,"detail_data")

            except Exception as e:
                print(f"{job_id} - Failed to fetch invoice detail for {invoice_id}: {e}")
                continue

            line_items = detail_data.get("LineItems", [])
            if not line_items:
                print(f"{job_id} - No line items found for invoice {invoice_id}")
                continue

            amounttx = "TaxInclusive" if item.get("AmountTaxStatus") in [3, "3"] else "TaxExclusive"


            for line in line_items:
                print(f"{job_id} - Processing line item for invoice {invoice_id}")

                QuerySet1 = {
                    "creditnotes_id": item.get("Id"),
                    "CashbookID": item.get("CashbookId"),
                    "creditnotes_number": item.get("CreditNoteNumber"),
                    "CustomerID": item.get("CustomerId"),
                    "CustomerName": item.get("CustomerName"),
                    "creditnotesAmount": item.get("CreditNoteAmount"),
                    "creditnotesDate": item.get("CreditNoteDate"),
                    "Balance": item.get("Balance"),
                    "Status": item.get("Status"),
                    "Reference": item.get("Reference"),
                    "Notes": item.get("Notes"),
                    "IsOverdue": item.get("IsOverdue"),
                    "AmountTaxStatus": amounttx,

                    # Line item fields
                    "Line_Id": line.get("Id"),
                    "Line_Inv_Id": line.get("InvoiceId"),
                    "Lineitem_Description": line.get("Description"),
                    "Line_ChargeableItemId":line.get("ChargeableItemId"),
                    "Lineitem_Quantity": line.get("Quantity"),
                    "LineProjectId": line.get("ProjectId",""),
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







def get_reckon_invoice_payment_excel(job_id, task_id):
    import traceback
    import requests
    import pandas as pd


    try:
        print(f"{job_id} - Inside get_reckon_invoice_excel")

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
        collection = dbname["reckon_invoice_payment_excel"]

        url = f"{base_url}/receipts"


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
            detail_url = f"{base_url}/receipts/{invoice_id}"
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
