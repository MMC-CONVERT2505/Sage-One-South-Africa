import json
import requests
from apps.mmc_settings.all_settings import get_settings_reckon
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.log_file import log_config


def add_excel_reckon_ytd_company_contributions(job_id,task_id):
    print("inside add_excel_reckon_ytd_company_contributions ****1")
    logging = log_config(job_id)
    try:

        logging.info(f"{job_id} inside add_excel_reckon_ytd_company_contributions")
        dbname=get_mongodb_database()
        payload, base_url, headers,book,post_headers,get_headers = get_settings_reckon(job_id)

        url = f"{base_url}/payroll/ytds/grosspays/details"
        logging.info(f"{job_id} add_excel_reckon_ytd_company_contributions--> url-->{url}")

        excel_reckon_company_contributions = dbname['get_excel_ytds_company_contributions']
        x = excel_reckon_company_contributions.find({"job_id":job_id})
        excel_reckon_company_contributions1 = []
        for k in x:
            excel_reckon_company_contributions1.append(k)
        for i in range(0,len(excel_reckon_company_contributions1)):
            _id=excel_reckon_company_contributions1[i]['_id']
            excel_reckon_company_contributions1[i].pop("_id")
            excel_reckon_company_contributions1[i].pop("job_id")
            excel_reckon_company_contributions1[i].pop("task_id")
            excel_reckon_company_contributions1[i].pop("is_pushed")
            excel_reckon_company_contributions1[i].pop("error")
            excel_reckon_company_contributions1[i].pop("payload")
            payload = json.dumps(excel_reckon_company_contributions1[i])

            print("payload>>>> inside write function  ***2",payload)
            
            asyncio.run(post_data_in_reckon(url, post_headers, payload,excel_reckon_company_contributions,_id, job_id,task_id, excel_reckon_company_contributions1[i]["PayItem"]))
           
                    
    except Exception as ex:
        import traceback
        traceback.print_exc()
        logging.error(ex, exc_info=True)