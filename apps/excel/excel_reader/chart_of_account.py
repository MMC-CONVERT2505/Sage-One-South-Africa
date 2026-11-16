import traceback
import os
import pandas as pd
import openpyxl

from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from flask.helpers import get_root_path


def get_excel_chart_of_account(job_id, task_id):
    try:
        dbname = get_mongodb_database()
        collection = dbname["excel_chart_of_account"]

        file_prefix = str(job_id)
        files_directory = os.path.join(get_root_path('apps'), 'files/')
        filename = next((f for f in os.listdir(files_directory) if f.startswith(file_prefix)), None)
        if filename is None:
            return

        path = os.path.join(files_directory, filename)
        workbook = openpyxl.load_workbook(path)
        sheet_names = workbook.sheetnames
        coa_data = pd.read_excel(path, 'COA')

        tax_codes = dbname["taxcode_myob"].find({"job_id": job_id})
        tax_code_map = {code["Code"]: code["UID"] for code in tax_codes}

        chart_of_accounts = dbname["chart_of_account"].find({"job_id": job_id})
        coa_map = {coa['DisplayId']: coa for coa in chart_of_accounts}

        

        for index, row in coa_data.iterrows():
            print(row["Parent Account Number"])
            print(type(row["Parent Account Number"]))
            tax_code = {}
            parent_account = {}

            tax_code["UID"] = tax_code_map.get(row["Tax Code"], tax_code_map.get("N-T"))
            tax_code["Code"] = row["Tax Code"]

            coa = coa_map.get(row["Parent Account Number"], {})
            parent_account["UID"] = coa.get("UID")
            parent_account["Name"] = coa.get("Name")
            parent_account["DisplayID"] = coa.get("DisplayId")

            is_header = row["Header"] == "H"

            coa_payload = {
                "job_id": job_id,
                "task_id": task_id,
                "is_pushed": 0,
                "payload": "",
                "error": "",
                "Name": row["Account Name"],
                "Classification": row["Classification"],
                "DisplayID": str(row['Account Number']),
                "Type": row['Account Type'],
                "Number": str(row['Account Number'].split("-")[1]),
                "TaxCode": tax_code,
                "IsHeader": is_header,
                "ParentAccount": str(row["Parent Account Number"])
            }

            collection.insert_one(coa_payload)

    except Exception as ex:
        traceback.print_exc()
