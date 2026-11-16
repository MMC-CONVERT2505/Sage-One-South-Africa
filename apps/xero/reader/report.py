import logging
from datetime import *
from apps.util.db_mongo import get_mongodb_database
import pandas as pd

logger = logging.getLogger(__name__)

def xero_ar_report(job_id,task_id):
    try:
        dbname = get_mongodb_database()
       
        xero_AR1 = dbname["xero_AR"].find({"job_id":job_id})
        xero_AP1 = dbname["xero_AP"].find({"job_id":job_id})

        xero_AR = []
        for p1 in xero_AR1:
            xero_AR.append(p1)

        xero_AP = []
        for p1 in xero_AP1:
            xero_AP.append(p1)

        selected_columns = ['ContactName', 'xero_balance', 'qbo_balance']  # Replace with the names of the columns you want
        xero_AR1 = pd.DataFrame(xero_AR, columns=selected_columns)
        xero_AP1 = pd.DataFrame(xero_AP, columns=selected_columns)
        excel_file = '/home/mahesh/Downloads/xero_comparison_report.xlsx'  # Replace with your desired Excel file name

        with pd.ExcelWriter(excel_file) as writer:
            xero_AR1.to_excel(writer, sheet_name="AR Comparison Report", index=False)
            xero_AP1.to_excel(writer, sheet_name="AP Comparison Report", index=False)

        print(f"Data exported to {excel_file}")
        
            
    except Exception as ex:
        logger.error("Error in xero -> qbowriter -> add_xero_invoice_payment", ex)

