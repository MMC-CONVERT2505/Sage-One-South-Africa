import traceback
import os
import requests
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path
import math
from apps.util.qbo_util import instance_check


def get_excel_reckon_supplier(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_reckon_supplier"]
        
        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory)
                        if f.startswith(file_prefix)), None)
        if filename is None:
            return
        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        supplier_data = pd.read_excel(path, 'Supplier')
        
        instance_name = None

        for index, row in supplier_data.iterrows():
            print(index)
            supplier_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "error": None,
                "payload": None,
                "FirstNameBranchName": instance_check(instance_name,row['Display name']),
                "SurnameBusinessName": instance_check(instance_name,row['Display name']),
                "Description":instance_check(instance_name,row['Display name']),
                "Branch": instance_check(instance_name,row['Branch']),
                "Notes": instance_check(instance_name,row['Notes']),
                "IsActive": True if row['Status'] == 1 else False,
                "BusinessNumber1": instance_check(instance_name,row['ABN']),
                # "businessNumber2": None,
                # "businessNumber": None,
                "Addresses": [
                    {
                    "Line1":instance_check(instance_name,row['BUSINESS ADDRESS']),
                    "Suburb":instance_check(instance_name,row['BUSINESS ADDRESS Suburb']),
                    "State":instance_check(instance_name,row['BUSINESS ADDRESS State']),
                    "Postcode":None if instance_check(instance_name,row['BUSINESS ADDRESS Postcode'])==None else str(row['BUSINESS ADDRESS Postcode'])[0:4],
                    "Country":instance_check(instance_name,row['BUSINESS ADDRESS Country']),
                    "AddressType":"Business",
                    "IsInternational":False
                    },
                    {
                    "Line1":instance_check(instance_name,row['POSTAL ADDRESS']),
                        "Suburb":instance_check(instance_name,row['POSTAL ADDRESS Suburb']),
                        "State":instance_check(instance_name,row['POSTAL ADDRESS State']),
                        "Postcode":None if instance_check(instance_name,row['POSTAL ADDRESS Postcode'])==None else str(row['BUSINESS ADDRESS Postcode'])[0:4],
                        "Country":instance_check(instance_name,row['POSTAL ADDRESS Country']),
                        "AddressType":"Postal",
                        "IsInternational":False
                        }
                    #     {
                    #     "Line1":instance_check(instance_name,row['SHIPPING ADDRESS']),
                    #     # "Line2":
                    #     # "Line3":
                    #     # "Town":
                    #     "Suburb":instance_check(instance_name,row['SHIPPING ADDRESS Suburb']),
                    #     "State":instance_check(instance_name,row['SHIPPING ADDRESS State']),
                    #     "Postcode":instance_check(instance_name,row['SHIPPING ADDRESS Postcode']),
                    #     "Country":instance_check(instance_name,row['SHIPPING ADDRESS Country']),
                    #     "AddressType":"Shipping",
                    #     "IsInternational": False
                    # }
                    ],
                "PhoneNumber": instance_check(instance_name,row['Phone']),
                "MobileNumber": instance_check(instance_name,row['Mobile']),
                "FaxNumber": instance_check(instance_name,row['Fax']),
                "Website": instance_check(instance_name,row['Web']),
                "Email": instance_check(instance_name,row['Email']),
                "IsSupplier": True
            }
            collection.insert_one(supplier_payload)

    except Exception as ex:
        traceback.print_exc()
