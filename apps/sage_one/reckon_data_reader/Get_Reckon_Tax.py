import traceback
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def get_reckon_taxcode_excel(job_id, task_id):
    import traceback
    import pandas as pd
    import requests

    try:
        # MongoDB setup
        db = get_mongodb_database()
        collection = db["taxcode_reckon_excel"]
        # Fetch settings
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(job_id)
        # API URL
        url = f"{base_url}/taxgroups/2000-01-01"

        # GET Request
        response = requests.get(url, headers=get_headers, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        tax_groups = json_data.get("Items", []) if isinstance(json_data, dict) else json_data

        if not tax_groups:

            return

        records = []
        for tax in tax_groups:
            record = {
                "job_id": job_id,
                "task_id": task_id,
                "table_name": "taxcode_reckon",
                "error": None,
                "is_pushed": 0,

                "ID": tax.get("ID"),
                "Name": tax.get("Name"),
                "Rate": tax.get("Rate"),
                "UseOnPurchases": tax.get("UseOnPurchases"),
                "UseOnSales": tax.get("UseOnSales"),
                "ExportCode": tax.get("ExportCode"),
                "Description": tax.get("Description"),
                "TaxReportingLocations": tax.get("TaxReportingLocations"),
            }

            # Handle nested TaxCodes if available
            tax_codes = tax.get("TaxCodes", [])
            if tax_codes:
                code = tax_codes[0]
                record["UseCodeOnPurchases"] = code.get("UseCodeOnPurchases")
                record["UseCodeOnSales"] = code.get("UseCodeOnSales")

            records.append(record)

        # Insert into MongoDB
        if records:
            collection.insert_many(records)


        # # Optional: Save to Excel
        # output_path = f"/home/ubuntu/output/taxcodes_reckon_{job_id}.xlsx"
        # df = pd.DataFrame(records)
        # df.to_excel(output_path, index=False)


    except Exception as ex:
        traceback.print_exc()
