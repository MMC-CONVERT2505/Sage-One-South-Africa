import traceback
import os
import requests
import pandas as pd
import openpyxl
import math

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
from apps.util.qbo_util import instance_check


def get_excel_supplier(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_supplier"]
        payload, base_url, headers = get_settings_myob(job_id)
        url = f"{base_url}/GeneralLedger/TaxCode"
        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()
        tax_codes = json_response["Items"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        supplier_data = pd.read_excel(path, 'Supplier')

        instance_name=None
        
        for index, row in supplier_data.iterrows():
            print(index)
            tax_code = {}
            for tax in tax_codes:
                if tax["Code"] == "N-T":
                    tax_code["UID"] = tax["UID"]

            if row["Type"] == "Supplier":
                supplier_payload = {
                    "job_id": job_id,
                    "task_id": task_id,
                    "is_pushed": 0,
                    "error": None,
                    "payload": None,
                    "CompanyName": str(instance_check(instance_name,row['Name']))[0:50] if instance_check(instance_name,row['Name'])!=None else None,
                    "IsIndividual": False,
                    "DisplayID": row["Contact ID"],
                    "Addresses": [
                        {
                            "Street": instance_check(instance_name,row['Street']),
                            "City": instance_check(instance_name,row['City']),
                            "State": instance_check(instance_name,row['State']),
                            "PostCode": str(int(row['Postcode'])) if instance_check(instance_name,row['Postcode'])!= None else None,
                            "Country": instance_check(instance_name,row['Country']),
                            "Phone1": instance_check(instance_name,row['Phone']),
                            "Fax": instance_check(instance_name,row['Fax']),
                            "Email": instance_check(instance_name,row['Email']),
                            "Website": instance_check(instance_name,row['WWW']),
                            "ContactName": str(instance_check(instance_name,row['Contact name']))[0:25] if instance_check(instance_name,row['Contact name'])!=None else None,
                            "Salutation": str(instance_check(instance_name,row['Memo']))[0:11].upper() if instance_check(instance_name,row['Memo'])!=None else None
                        },
                        {
                            "Street": instance_check(instance_name,row['Ship Street']),
                            "City": instance_check(instance_name,row['Ship City']),
                            "State": instance_check(instance_name,row['Ship State']),
                            "PostCode": str(int(instance_check(instance_name,row['Ship Postcode']))) if instance_check(instance_name,row['Ship Postcode'])!=None else None ,
                            "Country": instance_check(instance_name,row['Ship Country']),
                        }            
                    ],
                    
                    "Notes": instance_check(instance_name,row['Notes']),
                        
                    "PaymentDetails": {
                        "BSBNumber": instance_check(instance_name,row['BSB number']) ,
                        "BankAccountNumber": instance_check(instance_name,row['Bank acct No.']),
                        "BankAccountName": str(instance_check(instance_name,row['Bank acct name'])).upper() if instance_check(instance_name,row['Bank acct name'])!= None else None,
                        "StatementText": instance_check(instance_name,row['Memo']) 
                    },
                    "BuyingDetails": {
                        "ABN" : str(int(instance_check(instance_name,row['ABN']))) if instance_check(instance_name,row['ABN'])!=None else None,
                        "TaxCode": tax_code,
                        "FreightTaxCode": tax_code
                    }
                    }
        
                collection.insert_one(supplier_payload)

    except Exception as ex:
        traceback.print_exc()
        