import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config
from apps.home.data_util import get_job_details


def add_invoice_payment(job_id, task_id):
    logging =  log_config(job_id)
    print("inside add invoice payment")
    try:
        logging.info(f"{job_id} inside add_invoice_payment")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/receipts"

        sage_invoice_paymnet = dbname['sage_invoice_payment']

        x = sage_invoice_paymnet.find({"job_id": job_id,"is_pushed":0})
        sage_invoice_payment1 = []
        for k in x:
            sage_invoice_payment1.append(k)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)

        sage_bank_account = dbname["sage_bank"].find({"job_id": job_id})
        sage_bank_account1 = []
        for c002 in sage_bank_account:
            sage_bank_account1.append(c002)

        sage_customer = dbname["sage_customer"].find({"job_id": job_id})
        sage_customer1 = []
        for c2 in sage_customer:
            sage_customer1.append(c2)

        sage_bank_transaction = dbname["sage_bank_transaction"].find({"job_id": job_id})
        sage_bank_transaction1 = []
        for c3 in sage_bank_transaction:
            sage_bank_transaction1.append(c3)
        
        sage_invoice = dbname["sage_invoice"].find({"job_id": job_id})
        sage_invoice1 = []
        for c6 in sage_invoice:
            sage_invoice1.append(c6)


        sage_allocation_data = dbname["sage_allocation"].find({"job_id": job_id})
        sage_allocation1 = []
        for c4 in sage_allocation_data:
            sage_allocation1.append(c4)

        reckon_customer = dbname['reckon_customer']
        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)

        reckon_bank_account = dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank_account1 = []
        for p1 in reckon_bank_account:
            reckon_bank_account1.append(p1)

        reckon_invoice = dbname["reckon_invoice"].find({"job_id": job_id})
        reckon_invoice1 = []
        for p02 in reckon_invoice:
            reckon_invoice1.append(p02)

        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p04 in reckon_coa:
            reckon_coa1.append(p04)

        for i in range(0, len(sage_invoice_payment1)):
            start_date,end_date=get_job_details(job_id)
            if start_date <= sage_invoice_payment1[i]["Date"] and end_date >= sage_invoice_payment1[i]["Date"]:
        
                _id = sage_invoice_payment1[i]["_id"]
                QuerySet1 = {"Allocations": [],"AllocationSplit":[]}
                QuerySet1["TransDate"]= sage_invoice_payment1[i].get("Date",None)
                QuerySet1["Amount"]= sage_invoice_payment1[i].get("Total",None)

                for p in range(0,len(sage_bank_account1)):
                    bank_account_id={}
                    if sage_invoice_payment1[i].get("BankAccountId") == sage_bank_account1[p]["ID"]:
                        for q in range(0,len(reckon_bank_account1)):
                            if sage_bank_account1[p]["Name"].lower().strip() == reckon_bank_account1[q]["Description"].lower().strip():
                                QuerySet1["BankAccountId"]=reckon_bank_account1[q]["BankAccountID"]

                for k in range(0,len(reckon_customer1)):
                    for l in range(0,len(sage_customer1)):
                        if sage_invoice_payment1[i]["CustomerId"]==sage_customer1[l]["ID"]:
                            if sage_customer1[l]["Name"].lower().strip() == reckon_customer1[k]["Description"].lower().strip():
                                QuerySet1["ContactId"]=reckon_customer1[k]["ContactId"]
                            #     break
                            # else:
                            #     QuerySet1["ContactId"]="00000000-0000-0000-0000-000000000000"

                            

                for e in range(0,len(reckon_coa1)):
                    if "Accounts Receivable" in reckon_coa1[e]["Name"]:
                        QuerySet1["AccountsReceivableCategoryId"]=reckon_coa1[e]["Id"]
                        
                QuerySet1["Reference"]=sage_invoice_payment1[i].get("Reference",None)

                for r in range(0,len(sage_allocation1)):
                    
                    if sage_invoice_payment1[i].get("ID") == sage_allocation1[r]["SourceDocumentId"]:
                        for t in range(0,len(sage_invoice1)):

                            if sage_allocation1[r]["AllocatedToDocumentId"] == sage_invoice1[t]["ID"]:
                                
                                for m in range(0,len(reckon_invoice1)):
                                    reference_data=str(sage_invoice1[t].get("DocumentNumber"))+"-"+str(sage_invoice1[t].get("Reference",None))
                                    sage_documentNumber=reference_data[0:50]

                                    reference_data_id=str(sage_invoice1[t].get("ID")) + "-" + str(sage_invoice1[t].get("Reference", ""))
                                    sage_documentid = reference_data_id[0:50]
                                    lineitem={}
                                    if sage_documentNumber == reckon_invoice1[m]["Reference"]:
                                        lineitem["AllocationAmount"]= sage_allocation1[r]["Total"]
                                        lineitem["AllocationTypeId"]=1
                                        lineitem["RefId"] = reckon_invoice1[m]["Id"]
                                        QuerySet1["Allocations"].append(lineitem)
                                        break
                                    elif sage_documentid == reckon_invoice1[m]["Reference"]:

                                        lineitem={}
                                        lineitem["AllocationAmount"]= sage_allocation1[r]["Total"]
                                        lineitem["AllocationTypeId"]=1
                                        lineitem["RefId"] = reckon_invoice1[m]["Id"]
                                        QuerySet1["Allocations"].append(lineitem)


                payload = json.dumps(QuerySet1)
                print(payload,"payload ==========")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_invoice_paymnet,
                            _id, job_id, task_id, sage_invoice_payment1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
