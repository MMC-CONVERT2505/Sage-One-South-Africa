import traceback
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
import math
from apps.util.qbo_util import instance_check


def get_excel_customer(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_customer"]
        payload, base_url, headers = get_settings_myob(job_id)
        url = f"{base_url}/GeneralLedger/TaxCode"
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        print(json_response)
        tax_codes = json_response["Items"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        customer_data = pd.read_excel(path, 'Customer')

        instance_name=None
        
        for index, row in customer_data.iterrows():
            tax_code = {}
            for tax in tax_codes:
                if tax["Code"] == "N-T":
                    tax_code["UID"] = tax["UID"]

            if row["Type"] == "Customer":
                customer_payload = {
                    "job_id": job_id,
                    "task_id": task_id,
                    "is_pushed": 0,
                    "error":None,
                    "payload":None,
                    "CompanyName": str(instance_check(instance_name,row['Name']))[0:50] if instance_check(instance_name,row['Name'])!=None else None,
                    "IsIndividual": False,
                    "DisplayID": row["Contact ID"],
                    "Addresses": [
                        {
                            "Street": instance_check(instance_name,row['Street']),
                            "City": instance_check(instance_name,row['City']),
                            "State": instance_check(instance_name,row['State']),
                            "PostCode": str(int(row['Postcode'])) if instance_check(instance_name,row['Postcode'])!=None else None,
                            "Country": instance_check(instance_name,row['Country']),
                            "Phone1": instance_check(instance_name,row['Phone']),
                            "Fax": instance_check(instance_name,row['Fax']),
                            "Email": instance_check(instance_name,row['Email']),
                            "Website": instance_check(instance_name,row['WWW']),
                            "ContactName": str(instance_check(instance_name,row['Contact name']))[0:25] if instance_check(instance_name,row['Contact name'])!=None else None,
                            "Salutation": instance_check(instance_name,row['Memo'])
                        },
                        {
                            "Street": instance_check(instance_name,row['Ship Street']),
                            "City": instance_check(instance_name,row['Ship City']),
                            "State": instance_check(instance_name,row['Ship State']),
                            "PostCode": str(int(row['Ship Postcode'])) if instance_check(instance_name,row['Ship Postcode'])!=None else None,
                            "Country": instance_check(instance_name,row['Ship Country']),
                        }
                                    
                    ],
                    "Notes": instance_check(instance_name,row['Notes']),
                    "SellingDetails": {
                        "TaxCode": tax_code,
                        "FreightTaxCode": tax_code
                    }
                }
                collection.insert_one(customer_payload)

    except Exception as ex:
        traceback.print_exc()
