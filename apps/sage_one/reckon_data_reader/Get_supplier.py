import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon,get_settings_reckon_v2
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

# def get_reckon_supplier(job_id,task_id):
#     try:
#         db = get_mongodb_database()
#         Collection = db["reckon_supplier"]
#         no_of_records = db["reckon_supplier"].count_documents({"job_id":job_id})
#         payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

#         url = f"{base_url}/contacts/150000"
#         print(url)

#         response = requests.request("GET", url, headers=get_headers, data=payload)
#         JsonResponse1 = response.json()
#         JsonResponse = JsonResponse1['Items'] 

#         arr = []
#         for i in range(0, len(JsonResponse)):
#             QuerySet = {}
#             QuerySet["job_id"] = job_id
#             QuerySet["task_id"] = task_id
#             QuerySet['table_name'] = "reckon_contact"
#             QuerySet['error'] = None
#             QuerySet["is_pushed"] = 0
#             QuerySet["ContactId"] = JsonResponse[i]["ContactId"]
#             QuerySet["Description"] = JsonResponse[i]["Description"]
#             QuerySet["FirstNameBranchName"] = JsonResponse[i]["FirstNameBranchName"]
#             QuerySet["SurnameBusinessName"] = JsonResponse[i]["SurnameBusinessName"]
#             QuerySet["IsCustomer"] = JsonResponse[i]["IsCustomer"]
#             QuerySet["IsSupplier"] = JsonResponse[i]["IsSupplier"]
#             QuerySet["IsEmployee"] = JsonResponse[i]["IsEmployee"]
#             QuerySet["IsActive"] = JsonResponse[i]["IsActive"]


#             if JsonResponse[i]["IsSupplier"] != False:
            
#                 arr.append(QuerySet)

#         Collection.insert_many(arr)
#         print("Added")

#     except Exception as ex:
#         traceback.print_exc()






def get_reckon_supplier(job_id, task_id):
    try:
        db = get_mongodb_database()
        collection = db["reckon_supplier"]

        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon_v2(job_id)

        url = f"{base_url}/suppliers"
        print(url)

        response = requests.get(url, headers=get_headers)
        response.raise_for_status()

        arr=[]
        json_response = response.json()

        items = json_response.get("list", [])

        for item in items:
            if not item.get("entityTypes", {}).get("isSupplier", False):
                continue

            bank_details = item.get("bankDetails") or {}

                        # Electronic Addresses
            email = ""
            website = ""

            for e in item.get("electronicAddresses", []):
                if e.get("type", {}).get("name") == "Email":
                    email = e.get("address")
                elif e.get("type", {}).get("name") == "Web":
                    website = e.get("address")

            # Phone Numbers
            phone = ""
            mobile = ""
            fax = ""

            for p in item.get("phoneNumbers", []):
                type_name = p.get("type", {}).get("name")

                if type_name == "Phone":
                    phone = p.get("number")
                elif type_name == "Mobile":
                    mobile = p.get("number")
                elif type_name == "Fax":
                    fax = p.get("number")

            # Addresses
            business_address = {}
            postal_address = {}
            shipping_address = {}

            for a in item.get("addresses", []):
                type_name = a.get("type", {}).get("name")

                if type_name == "Business":
                    business_address = a
                elif type_name == "Postal":
                    postal_address = a
                elif type_name == "Shipping":
                    shipping_address = a

            # Contact
            contact_name = ""
            if item.get("contacts"):
                contact_name = item["contacts"][0].get("name", "")

            record = {
                "job_id": job_id,
                "task_id": task_id,
                "table_name": "reckon_supplier",
                "error": None,
                "is_pushed": 0,

                "ContactId": item.get("id"),
                "Name": item.get("name"),
                "OrganisationName": item.get("organisationName"),
                "Branch": item.get("branch"),
                "Status": item.get("status"),

                "IsCustomer": item.get("entityTypes", {}).get("isCustomer"),
                "IsSupplier": item.get("entityTypes", {}).get("isSupplier"),
                "IsEmployee": item.get("entityTypes", {}).get("isEmployee"),
                "IsSuperfund": item.get("entityTypes", {}).get("isSuperfund"),

                "Notes": item.get("notes"),
                "BusinessNumber": item.get("businessNumber"),
                "BusinessNumber1": item.get("businessNumber1"),
                "BusinessNumber2": item.get("businessNumber2"),

                "Email": email,
                "Website": website,

                "Phone": phone,
                "Mobile": mobile,
                "Fax": fax,

                "BusinessLine1": business_address.get("line1"),
                "BusinessLine2": business_address.get("line2"),
                "BusinessSuburb": business_address.get("suburb"),
                "BusinessTown": business_address.get("town"),
                "BusinessState": business_address.get("state"),
                "BusinessPostcode": business_address.get("postcode"),
                "BusinessCountry": business_address.get("country"),

                "PostalLine1": postal_address.get("line1"),
                "PostalLine2": postal_address.get("line2"),
                "PostalSuburb": postal_address.get("suburb"),
                "PostalTown": postal_address.get("town"),
                "PostalState": postal_address.get("state"),
                "PostalPostcode": postal_address.get("postcode"),
                "PostalCountry": postal_address.get("country"),

                "ShippingLine1": shipping_address.get("line1"),
                "ShippingLine2": shipping_address.get("line2"),
                "ShippingSuburb": shipping_address.get("suburb"),
                "ShippingTown": shipping_address.get("town"),
                "ShippingState": shipping_address.get("state"),
                "ShippingPostcode": shipping_address.get("postcode"),
                "ShippingCountry": shipping_address.get("country"),

                "ContactName": contact_name,


                "Balance": item.get("balance"),
                "LastModifiedDateTime": item.get("lastModifiedDateTime"),
                "IsTPAR": item.get("isTpar"),

                "BankName": bank_details.get("name"),
                "BankBranchNumber": bank_details.get("bankBranchNumber"),
                "BankAccountNumber": bank_details.get("bankAccountNumber"),
            }

            arr.append(record)

        if arr:
            collection.insert_many(arr)

        print(f"{len(arr)} suppliers added.")

    except Exception:
        traceback.print_exc()


def get_reckon_common_customer(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_reckon_comman_customer-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        
        collection = dbname["reckon_comman_customer"]

        sage_comman_contact = dbname['sage_comman_contact']

        x = sage_comman_contact.find({"job_id": job_id})
        sage_comman_contact1 = []
        for k in x:
            sage_comman_contact1.append(k)

        reckon_supplier = dbname['reckon_supplier']

        x = reckon_supplier.find({"job_id": job_id})
        reckon_supplier1 = []
        for k in x:
            reckon_supplier1.append(k)
        
        arr=[]

        for i in range(0,len(sage_comman_contact1)):
            for j in range(0,len(reckon_supplier1)):

                if reckon_supplier1[j]["Description"]==sage_comman_contact1[i]["Name"]:
                    print(reckon_supplier1[j]["Description"],"reckon_supplier1")
                    QuerySet = {}
                    QuerySet["job_id"] = job_id
                    QuerySet["task_id"] = task_id
                    QuerySet['table_name'] = "reckon_comman_customer"
                    QuerySet['error'] = None
                    QuerySet["is_pushed"] = 0
                    QuerySet["ContactId"] = reckon_supplier1[j]["ContactId"]
                    QuerySet["Description"] = reckon_supplier1[j]["Description"]
                    QuerySet["FirstNameBranchName"] = reckon_supplier1[j]["FirstNameBranchName"]
                    QuerySet["SurnameBusinessName"] = reckon_supplier1[j]["SurnameBusinessName"]
                    QuerySet["IsCustomer"] = True
                    QuerySet["IsSupplier"] = reckon_supplier1[j]["IsSupplier"]
                    QuerySet["IsEmployee"] = reckon_supplier1[j]["IsEmployee"]
                    QuerySet["IsActive"] = reckon_supplier1[j]["IsActive"]


                    
                    arr.append(QuerySet)

        collection.insert_many(arr)
        print("Added")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

def get_reckon_common_supplier(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_reckon_comman_supplier-------------updated")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        
        collection = dbname["reckon_comman_supplier"]

        sage_comman_contact_customer = dbname['sage_comman_contact_customer']

        x = sage_comman_contact_customer.find({"job_id": job_id})
        sage_comman_contact_customer1 = []
        for k in x:
            sage_comman_contact_customer1.append(k)

        reckon_customer = dbname['reckon_customer']

        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)
        
        arr=[]

        for i in range(0,len(sage_comman_contact_customer1)):
            for j in range(0,len(reckon_customer1)):

                if reckon_customer1[j]["Description"]==sage_comman_contact_customer1[i]["Name"]:
                    print(reckon_customer[j]["Description"],"reckon_supplier1")
                    QuerySet = {}
                    QuerySet["job_id"] = job_id
                    QuerySet["task_id"] = task_id
                    QuerySet['table_name'] = "reckon_comman_customer"
                    QuerySet['error'] = None
                    QuerySet["is_pushed"] = 0
                    QuerySet["ContactId"] = reckon_customer1[j]["ContactId"]
                    QuerySet["Description"] = reckon_customer1[j]["Description"]
                    QuerySet["FirstNameBranchName"] = reckon_customer1[j]["FirstNameBranchName"]
                    QuerySet["SurnameBusinessName"] = reckon_customer1[j]["SurnameBusinessName"]
                    QuerySet["IsCustomer"] = reckon_customer1[j]["IsCustomer"]
                    QuerySet["IsSupplier"] = True
                    QuerySet["IsEmployee"] = reckon_customer1[j]["IsEmployee"]
                    QuerySet["IsActive"] = reckon_customer1[j]["IsActive"]


                    
                    arr.append(QuerySet)

        collection.insert_many(arr)
        print("Added")

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)