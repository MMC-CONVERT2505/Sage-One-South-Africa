import traceback
from ast import Break
import requests
import json
from apps.home.data_util import add_job_status
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config
import datetime
from datetime import datetime, timedelta

def get_sage_report_comman_customer_balance(job_id,task_id):
    print("inside get sage report customer balance data===========")
    try:
        dbname = get_mongodb_database()
        Collection = dbname["sage_report_comman_customer_balance"]

        sage_opeing_customer_balance = dbname["sage_opening_customer"].find({"job_id":job_id})
        sage_opeing_customer_balance1 = []
        for p4 in sage_opeing_customer_balance:
            sage_opeing_customer_balance1.append(p4)

        sage_customer = dbname["sage_customer"].find({"job_id":job_id})
        sage_customer1 = []
        for p5 in sage_customer:
            sage_customer1.append(p5)
        
        match_customer=[]
        for i in range(0,len(sage_opeing_customer_balance1)):
            for j in range(0,len(sage_customer1)):
                if sage_opeing_customer_balance1[i]["CustomerId"] == sage_customer1[j]["ID"]:
                    if sage_customer1[j]["Balance"] != 0:
                        Collection.insert_one(match_customer)
        
        
    except Exception as ex:
        traceback.print_exc()
        


