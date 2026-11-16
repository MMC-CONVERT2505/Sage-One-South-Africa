import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config
from apps.home.data_util import get_job_details, add_job_status


def add_reckon_bank_transfer(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_bank_transfer ")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/banktransfers"

        sage_bank_transfer = dbname['sage_bank_transfer']
        logging.info(f"{job_id} add_reckon_bank_transfer--> url --> {url}")
        x = sage_bank_transfer.find({"job_id": job_id,"is_pushed":0})
        sage_bank_transfer1 = []
        for k in x:
            sage_bank_transfer1.append(k)

        
        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)
        
        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p1 in reckon_coa:
            reckon_coa1.append(p1)

   

        sage_bank_account = dbname["sage_bank"].find({"job_id": job_id})
        sage_bank_account1 = []
        for c002 in sage_bank_account:
            sage_bank_account1.append(c002)

        reckon_bank_account = dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank_account1 = []
        for p1 in reckon_bank_account:
            reckon_bank_account1.append(p1)

        for i in range(0, len(sage_bank_transfer1)):
            start_date,end_date=get_job_details(job_id)

            if sage_bank_transfer1[i]["Total"]>0 and sage_bank_transfer1[i]["Type"]==4:
                if start_date <= sage_bank_transfer1[i]["Date"] and end_date >= sage_bank_transfer1[i]["Date"]:
                    _id = sage_bank_transfer1[i]["_id"]
                    QuerySet1={}
                    QuerySet1["TransferDate"]=sage_bank_transfer1[i].get("Date")
                    QuerySet1["Description"]=sage_bank_transfer1[i].get("Description",None)
                    QuerySet1["Amount"]=abs(sage_bank_transfer1[i].get("Total"))

                    for m1 in range(0,len(sage_bank_account1)):
                        if sage_bank_transfer1[i].get("BankAccountId")== sage_bank_account1[m1]["ID"]:
                            for q1 in range(0,len(reckon_bank_account1)):
                                if sage_bank_account1[m1]["Name"].lower() == reckon_bank_account1[q1]["Description"].lower():
                                    QuerySet1["ToBankAccountId"]=reckon_bank_account1[q1]["BankAccountID"]
                                    QuerySet1["ToReconciliationStatus"]=1
                                    break

                    for m in range(0,len(sage_bank_account1)):
                        if sage_bank_transfer1[i].get("SelectionId") == sage_bank_account1[m]["ID"]:
                            for q in range(0,len(reckon_bank_account1)):
                                if sage_bank_account1[m]["Name"].lower() == reckon_bank_account1[q]["Description"].lower():
                                    QuerySet1["FromBankAccountId"]=reckon_bank_account1[q]["BankAccountID"]
                                    QuerySet1["FromReconciliationStatus"]=1
                                    break

                    payload = json.dumps(QuerySet1)
                    
                    asyncio.run(post_data_in_reckon(url, post_headers, payload,
                            sage_bank_transfer, _id, job_id, task_id, sage_bank_transfer1[i]["ID"]))
                # else:
                #     _id = sage_bank_transfer1[i]["_id"]
                #     sage_bank_transfer.update_one({'_id': _id}, {"$set": {"payload":"Out of date"}}, upsert=True)
            
                
            # else:
            #     _id = sage_bank_transfer1[i]["_id"]
            #     sage_bank_transfer.update_one({'_id': _id}, {"$set": {"payload":"Total < 0"}}, upsert=True)
            #     print("Total < 0")
                
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
