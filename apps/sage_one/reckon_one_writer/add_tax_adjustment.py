import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_journal_as_a_tax_adjustment(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_journal_as_a_tax_adjustment")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/journals"

        sage_tax_adjustment = dbname['sage_tax_adjustment']

        x = sage_tax_adjustment.find({"job_id": job_id,"is_pushed":0})
        sage_tax_adjustment1 = []
        for k in x:
            sage_tax_adjustment1.append(k)

        
        reckon_customer = dbname['reckon_customer']
        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)

        sage_customer = dbname['sage_customer']
        x = sage_customer.find({"job_id": job_id})
        sage_customer1 = []
        for i in x:
            sage_customer1.append(i)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)
        
        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p1 in reckon_coa:
            reckon_coa1.append(p1)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        for i in range(0, len(sage_tax_adjustment1)):

            if sage_tax_adjustment1[i]["TaxAdjustmentType"] == 1 and sage_tax_adjustment1[i]["TaxAdjustmentAccountType"] != 2:
                logging.info(f"{job_id} inside sage journal as tax adjustment data ")
                _id = sage_tax_adjustment1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_tax_adjustment1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                QuerySet1["JournalNumber"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["FullDescription"]=sage_tax_adjustment1[i].get("Description",None)
                QuerySet1["Summary"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["AmountTaxStatus"]=3

                
                if sage_tax_adjustment1[i].get("Total")> 0:
                    transactionlinedebit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinedebit["AccountingCategoryId"]=None


                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                    transactionlinecredit={}
                
                    for e in range(0,len(sage_coa1)):
                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in  ["Opening Balance","Tax Adjustments"]:
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None


                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    payload = json.dumps(QuerySet1)

                elif sage_tax_adjustment1[i].get("Total")< 0:
                    transactionlinecredit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinecredit["AccountingCategoryId"]=None

                
                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    transactionlinedebit={}

                    for e in range(0,len(sage_coa1)):

                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in ["Opening Balance","Tax Adjustments"]:
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Exclusive",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                    
                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                payload = json.dumps(QuerySet1)
                print(payload,"payload data ======================")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_tax_adjustment,
                            _id, job_id, task_id, sage_tax_adjustment1[i]["ID"]))
                
            elif sage_tax_adjustment1[i]["TaxAdjustmentType"] == 2 and sage_tax_adjustment1[i]["TaxAdjustmentAccountType"] != 2:
                logging.info(f"{job_id} inside sage journal as tax adjustment output tax data ")
                _id = sage_tax_adjustment1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_tax_adjustment1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                QuerySet1["JournalNumber"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["FullDescription"]=sage_tax_adjustment1[i].get("Description",None)
                QuerySet1["Summary"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["AmountTaxStatus"]=3

                
                if sage_tax_adjustment1[i].get("Total")> 0:
                    transactionlinedebit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinedebit["AccountingCategoryId"]=None


                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                    transactionlinecredit={}
                
                    for e in range(0,len(sage_coa1)):
                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in  ["Opening Balance","Tax Adjustments"]:
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None


                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    payload = json.dumps(QuerySet1)

                elif sage_tax_adjustment1[i].get("Total")< 0:
                    transactionlinecredit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinecredit["AccountingCategoryId"]=None

                
                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    transactionlinedebit={}

                    for e in range(0,len(sage_coa1)):

                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in ["Opening Balance","Tax Adjustments"]:
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Exclusive",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                    
                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                payload = json.dumps(QuerySet1)
                print(payload,"payload data ======================")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_tax_adjustment,
                            _id, job_id, task_id, sage_tax_adjustment1[i]["ID"]))
            elif sage_tax_adjustment1[i]["TaxAdjustmentAccountType"] == 2 :
                logging.info(f"{job_id} inside sage journal as tax adjustment provisional tax data ")
                _id = sage_tax_adjustment1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_tax_adjustment1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                QuerySet1["JournalNumber"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["FullDescription"]=sage_tax_adjustment1[i].get("Description",None)
                QuerySet1["Summary"]=sage_tax_adjustment1[i].get("ID",None)
                QuerySet1["AmountTaxStatus"]=3

                
                if sage_tax_adjustment1[i].get("Total")> 0:
                    transactionlinedebit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinedebit["AccountingCategoryId"]=None


                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                    transactionlinecredit={}
                
                    for e in range(0,len(sage_coa1)):
                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in  ["Opening Balance","Tax Adjustments"]:
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None


                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    payload = json.dumps(QuerySet1)

                elif sage_tax_adjustment1[i].get("Total")< 0:
                    transactionlinecredit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[v]["Name"] == "Tax Payable":
                            transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            transactionlinecredit["Credit"]=abs(sage_tax_adjustment1[i].get("Total",0.0))
                            break
                        else:
                            transactionlinecredit["AccountingCategoryId"]=None

                
                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    transactionlinedebit={}

                    for e in range(0,len(sage_coa1)):

                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] in ["Opening Balance","Tax Adjustments"]:
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_tax_adjustment1[i].get("Exclusive",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                    
                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                payload = json.dumps(QuerySet1)
                print(payload,"payload data ======================")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_tax_adjustment,
                            _id, job_id, task_id, sage_tax_adjustment1[i]["ID"]))
                


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
