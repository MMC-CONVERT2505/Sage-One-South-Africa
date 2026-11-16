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

def add_bill_payment(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside add_bill_payment ")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/payments"
        sage_bill_paymnet = dbname['sage_bill_payment']
        sage_bill_paymnet_data = dbname['sage_bill_payment'].find({"job_id": job_id,"is_pushed":0})

        sage_bill_paymnet_data1 = []
        for k in sage_bill_paymnet_data:
            sage_bill_paymnet_data1.append(k)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)

        sage_bank_account = dbname["sage_bank"].find({"job_id": job_id})
        sage_bank_account1 = []
        for c002 in sage_bank_account:
            sage_bank_account1.append(c002)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

        sage_supplier = dbname["sage_supplier"].find({"job_id": job_id})
        sage_supplier1 = []
        for c2 in sage_supplier:
            sage_supplier1.append(c2)
        
        sage_bill = dbname["sage_bill"].find({"job_id": job_id})
        sage_bill1 = []
        for c6 in sage_bill:
            sage_bill1.append(c6)


        sage_allocation_data = dbname["sage_allocation"].find({"job_id": job_id})
        sage_allocation1 = []
        for c4 in sage_allocation_data:
            sage_allocation1.append(c4)

        reckon_supplier = dbname['reckon_supplier'].find({"job_id": job_id})
        reckon_supplier1 = []
        for k in reckon_supplier:
            reckon_supplier1.append(k)

        reckon_bank_account = dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank_account1 = []
        for p1 in reckon_bank_account:
            reckon_bank_account1.append(p1)

        reckon_bill = dbname["reckon_bill"].find({"job_id": job_id})
        reckon_bill1 = []
        for p02 in reckon_bill:
            reckon_bill1.append(p02)

        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p04 in reckon_coa:
            reckon_coa1.append(p04)

        for i in range(0, len(sage_bill_paymnet_data1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_bill_paymnet_data1[i]["Date"] and end_date >= sage_bill_paymnet_data1[i]["Date"]:
                logging.info(f"{job_id} inside sage invoice data")
                _id = sage_bill_paymnet_data1[i]["_id"]
                QuerySet1 = {"Allocations": [],"AllocationSplit":[]}
            
                QuerySet1["TransDate"]= sage_bill_paymnet_data1[i].get("Date",None)
                QuerySet1["Amount"]= sage_bill_paymnet_data1[i].get("Total",None)

                for p in range(0,len(sage_bank_account1)):
                    bank_account_id={}
                    if sage_bill_paymnet_data1[i].get("BankAccountId") == sage_bank_account1[p]["ID"]:
                        for q in range(0,len(reckon_bank_account1)):
                            if sage_bank_account1[p]["Name"].lower().strip() == reckon_bank_account1[q]["Description"].lower().strip():
                                QuerySet1["BankAccountId"]=reckon_bank_account1[q]["BankAccountID"]

                for k in range(0,len(reckon_supplier1)):
                    for l in range(0,len(sage_supplier1)):
                        if sage_bill_paymnet_data1[i]["SupplierId"]==sage_supplier1[l]["ID"]:
                            if sage_supplier1[l]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["ContactId"]=reckon_supplier1[k]["ContactId"]
                            
                            

                for e in range(0,len(reckon_coa1)):
                    if "Accounts Payable" in reckon_coa1[e]["Name"]:
                        logging.info(reckon_coa1[e]["Id"])
                        QuerySet1["AccountsPayableCategoryId"]=reckon_coa1[e]["Id"]
                        
                QuerySet1["Reference"]=sage_bill_paymnet_data1[i].get("Reference",None)


                for r in range(0,len(sage_allocation1)):
                    
                    if sage_bill_paymnet_data1[i].get("ID") == sage_allocation1[r]["SourceDocumentId"]:
                        
                        for t in range(0,len(sage_bill1)):
                            
                            if sage_allocation1[r]["AllocatedToDocumentId"] == sage_bill1[t]["ID"]:
                                
                                logging.info(f"{job_id} match allocation id")
                                for m in range(0,len(reckon_bill1)):
                                    reference_document=str(sage_bill1[t].get("DocumentNumber"))+"-"+str(sage_bill1[t].get("Reference",None))
                                    sage_documentNumber=reference_document[0:50]
                                    reference_id=str(sage_bill1[t].get("ID")) + "-" + str(sage_bill1[t].get("Reference", ""))
                                    sage_documentid = reference_id[0:50]
                                    lineitem={}
                                    if sage_documentNumber == reckon_bill1[m]["Reference"]:
                        
                                        lineitem["AllocationAmount"]= sage_allocation1[r]["Total"]
                                        lineitem["AllocationTypeId"]=2
                                        lineitem["RefId"] = reckon_bill1[m]["BillID"]
                                        QuerySet1["Allocations"].append(lineitem)
                                        break
                                    elif sage_documentid == reckon_bill1[m]["Reference"]:
                                    
                                        lineitem["AllocationAmount"]= sage_allocation1[r]["Total"]
                                        lineitem["AllocationTypeId"]=2
                                        lineitem["RefId"] = reckon_bill1[m]["BillID"]
                                        QuerySet1["Allocations"].append(lineitem)

                payload = json.dumps(QuerySet1)
                print(payload,"payload data")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_bill_paymnet,
                            _id, job_id, task_id, sage_bill_paymnet_data1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
