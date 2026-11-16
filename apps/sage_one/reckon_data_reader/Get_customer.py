import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_reckon_customer(job_id,task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_customer"]
        no_of_records = db["reckon_customer"].count_documents({"job_id":job_id})
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/contacts/20000"
        print(url)

        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse1 = response.json()
        JsonResponse = JsonResponse1['Items'] 

        arr = []
        for i in range(0, len(JsonResponse)):
            QuerySet = {}
            QuerySet["job_id"] = job_id
            QuerySet["task_id"] = task_id
            QuerySet['table_name'] = "reckon_contact"
            QuerySet['error'] = None
            QuerySet["is_pushed"] = 0
            QuerySet["ContactId"] = JsonResponse[i]["ContactId"]
            QuerySet["Description"] = JsonResponse[i]["Description"]
            QuerySet["FirstNameBranchName"] = JsonResponse[i]["FirstNameBranchName"]
            QuerySet["SurnameBusinessName"] = JsonResponse[i]["SurnameBusinessName"]
            QuerySet["IsCustomer"] = JsonResponse[i]["IsCustomer"]
            QuerySet["IsSupplier"] = JsonResponse[i]["IsSupplier"]
            QuerySet["IsEmployee"] = JsonResponse[i]["IsEmployee"]
            QuerySet["IsActive"] = JsonResponse[i]["IsActive"]

            if JsonResponse[i]["IsCustomer"] != False:
                arr.append(QuerySet)

        Collection.insert_many(arr)
        print("Added")

    except Exception as ex:
        traceback.print_exc()



def get_reckon_customer_data(job_id, task_id):
    try:
        db = get_mongodb_database()
        Collection = db["reckon_customer_data"]

        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/contacts/20000"
        print(url)

        response = requests.request("GET", url, headers=get_headers, data=payload)
        JsonResponse = response.json().get("Items", [])

        arr = []

        for i in range(len(JsonResponse)):
            item = JsonResponse[i]

            if item.get("IsCustomer") is not True:
                continue

            addresses = item.get("Addresses", [])

            # If no address → still insert one row
            if not addresses:
                addresses = [None]

            for addr in addresses:
                QuerySet = {}
                QuerySet["job_id"] = job_id
                QuerySet["task_id"] = task_id
                QuerySet["table_name"] = "reckon_contact"
                QuerySet["error"] = None
                QuerySet["is_pushed"] = 0

                # ------------------
                # CUSTOMER FIELDS
                # ------------------
                QuerySet["ContactId"] = item.get("ContactId")
                QuerySet["CashbookId"] = item.get("CashbookId")
                QuerySet["PaymentTermId"] = item.get("PaymentTermId")
                QuerySet["CustomerCreditLimit"] = item.get("CustomerCreditLimit")
                QuerySet["Description"] = item.get("Description")
                QuerySet["FirstNameBranchName"] = item.get("FirstNameBranchName")
                QuerySet["SurnameBusinessName"] = item.get("SurnameBusinessName")
                QuerySet["IsCustomer"] = item.get("IsCustomer")
                QuerySet["IsSupplier"] = item.get("IsSupplier")
                QuerySet["IsEmployee"] = item.get("IsEmployee")
                QuerySet["IsActive"] = item.get("IsActive")
                QuerySet["IsPerson"] = item.get("IsPerson")
                QuerySet["IsTpar"] = item.get("IsTpar")
                QuerySet["IsSuperfund"] = item.get("IsSuperfund")
                QuerySet["LastModifiedDate"] = item.get("LastModifiedDate")

                # ------------------
                # ADDRESS FIELDS (LINE-WISE)
                # ------------------
                if addr:
                    QuerySet["AddressId"] = addr.get("AddressId")
                    QuerySet["AddressType"] = addr.get("AddressType")
                    QuerySet["Line1"] = addr.get("Line1")
                    QuerySet["Line2"] = addr.get("Line2")
                    QuerySet["Line3"] = addr.get("Line3")
                    QuerySet["Town"] = addr.get("Town")
                    QuerySet["Suburb"] = addr.get("Suburb")
                    QuerySet["State"] = addr.get("State")
                    QuerySet["Postcode"] = addr.get("Postcode")
                    QuerySet["Country"] = addr.get("Country")
                    QuerySet["IsInternational"] = addr.get("IsInternational")
                else:
                    QuerySet["AddressId"] = None
                    QuerySet["AddressType"] = None

                arr.append(QuerySet)

        if arr:
            Collection.insert_many(arr)

        print(f"Inserted {len(arr)} records (address line-wise)")

    except Exception:
        traceback.print_exc()




def get_reckon_customer1(job_id, task_id):
    
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get _reckon_supplier-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        collection = dbname["reckon_customer"]
        # url = "https://api.reckon.com/r1//3c634d86-5913-4ae1-871c-94d91ec018b3/contacts"
        
        url = f"{base_url}/contacts"

        response = requests.request("GET", url, headers=get_headers, data=payload)
        print(response)
        JsonResponse1 = response.json()
        print(JsonResponse1)
        logging.info(f"{job_id} get_reckon_customer--> url --> {url} response status-->{response.status_code}")
        arr = []
        for item in JsonResponse1:

            item["job_id"] = job_id
            item["task_id"] = task_id
            item['table_name'] = "reckon_customer"
            item['error'] = None
            item["is_pushed"] = 0
            if item.get("IsCustomer") == True:
                arr.append(item)
                
            else:
                pass

            # Move the following line inside the loop
        collection.insert_many(arr)
        logging.info(f"{job_id} inserted_many data in reckon_customer")


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

# The rest of your code...
