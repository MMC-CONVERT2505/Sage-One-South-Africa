import traceback

import requests
import base64

from apps import db
from apps.home.models import Jobs
from apps.home.models import Tool, ToolSettings
# from apps.util.qbo_util import add_job_status
from apps.util.log_file import log_config

def get_sageone_settings(job_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside get_sageone_settings")
        keys = (
            db.session.query(Jobs, ToolSettings.keys, ToolSettings.values)
                .join(Tool, Jobs.input_account_id == Tool.id)
                .join(ToolSettings, ToolSettings.tool_id == Tool.id)
                .filter(Jobs.id == job_id)
                .all()
        )

        print(keys,"==============")
        for row in keys:
            if row[1] == "api_key":
                api_key = row[2]
            if row[1] == "company_id":
                company_id = row[2]
            if row[1] == "username":
                username = row[2]
            if row[1] == "password":
                password = row[2]

        credentials = f"{username}:{password}"


        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")


        payload = {} 

        api_key_data= api_key

        company_id_data=company_id
        base_url = "https://accounting.sageone.com.au/api/1.1.2"

        headers = {
                'Authorization': f"Basic {encoded_credentials}"
            }
        
        return payload, headers,api_key_data,company_id_data

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        
