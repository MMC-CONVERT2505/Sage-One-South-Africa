import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config

def get_sage_comman_customer(job_id,task_id):
    print("inside get sage comman customer data===========")
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside sage_comman_customer")
        dbname = get_mongodb_database()
        Collection = dbname["sage_comman_customer"]

        sage_customer = dbname['sage_customer']

        x = sage_customer.find({"job_id": job_id,"is_pushed":0})
        sage_customer1 = []
        for k in x:
            sage_customer1.append(k)


        sage_opening_customer = dbname['sage_opening_customer']

        p = sage_opening_customer.find({"job_id": job_id,"is_pushed":0})
        sage_opening_customer1 = []
        for k1 in p:
            sage_opening_customer1.append(k1)

        matched_customers = []

        for i in range(0, len(sage_customer1)):
            for j in range(0,len(sage_opening_customer1)):
                if sage_opening_customer1[j]["CustomerId"] == sage_customer1[i]["ID"]:
                    if sage_customer1[i]["Balance"] != 0:
                        matched_customers.append(sage_customer1[i])

                        if matched_customers:
                            Collection.insert_one(matched_customers)
                        

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
        


