import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.home.data_util import get_job_details
from apps.util.log_file import log_config

def add_journal_as_a_customer_write_off(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_journal_as_a_customer_write_off")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/journals"

        sage_customer_write_off = dbname['sage_customer_write_off']

        x = sage_customer_write_off.find({"job_id": job_id,"is_pushed":0})
        sage_customer_write_off1 = []
        for k in x:
            sage_customer_write_off1.append(k)

        
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

        for i in range(0, len(sage_customer_write_off1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_customer_write_off1[i]["Date"] and end_date >= sage_customer_write_off1[i]["Date"]:
           
                logging.info(f"{job_id} inside sage journal data")
                _id = sage_customer_write_off1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_customer_write_off1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                QuerySet1["JournalNumber"]=sage_customer_write_off1[i].get("DocumentNumber",None)
                QuerySet1["FullDescription"]=sage_customer_write_off1[i].get("Description",None)
                QuerySet1["Summary"]=sage_customer_write_off1[i].get("DocumentNumber",None)
                QuerySet1["AmountTaxStatus"]=3

                
                if sage_customer_write_off1[i].get("Total")> 0:
                    transactionlinedebit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[n]["Name"] == "Bad Debts":
                            transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            exclusive_taxamount=sage_customer_write_off1[i].get("Total",0.0) * 10 /110
                            transactionlinedebit["Debit"]=round((sage_customer_write_off1[i].get("Total",0.0))-(exclusive_taxamount),2)
                            transactionlinedebit["TaxAmount"]=round(exclusive_taxamount,2)
                            break
                        else:
                            transactionlinedebit["AccountingCategoryId"]=None

                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'GST':
                            tax_grp_id = taxcode_reckon[m]['ID']


                            
                    transactionlinedebit["TaxGroupId"] = tax_grp_id



                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                    transactionlinecredit={}
                
                    for p in range(0,len(sage_customer1)):
                        for m in range(0,len(reckon_customer1)):
                            if sage_customer_write_off1[i].get("CustomerId") == sage_customer1 [p]["ID"]:
                                if sage_customer1 [p]["Name"].lower() ==  reckon_customer1[m]["FirstNameBranchName"].lower():
                                    transactionlinecredit["ContactId"]=reckon_customer1[m]["ContactId"]
                    for e in range(0,len(sage_coa1)):
                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_customer_write_off1[i].get("Total",0.0))
                                transactionlinecredit["TaxAmount"]=0
                                
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']

                    transactionlinecredit["TaxGroupId"] = tax_grp_id


                    


                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    payload = json.dumps(QuerySet1)

                elif sage_customer_write_off1[i].get("Total")< 0:
                    transactionlinecredit={}
                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[n]["Name"] == "Bad Debts":
                            transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                            exclusive_taxamount=sage_customer_write_off1[i].get("Total",0.0) * 10 /110
                            transactionlinecredit["TaxAmount"]=round(exclusive_taxamount,2)
                           
                            transactionlinecredit["Credit"]=round((sage_customer_write_off1[i].get("Total",0.0))-(exclusive_taxamount),2)
                            break
                        else:
                            transactionlinecredit["AccountingCategoryId"]=None

                
                    transactionlinecredit["TransType"] = 2

                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'GST':
                            tax_grp_id = taxcode_reckon[m]['ID']
    
                    transactionlinecredit["TaxGroupId"] = tax_grp_id

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    transactionlinedebit={}

                    
                    for p in range(0,len(sage_customer1)):
                        for m in range(0,len(reckon_customer1)):
                            if sage_customer_write_off1[i].get("CustomerId") == sage_customer1 [p]["ID"]:
                                if sage_customer1 [p]["Name"].lower() ==  reckon_customer1[m]["FirstNameBranchName"].lower():
                                    transactionlinedebit["ContactId"]=reckon_customer1[m]["ContactId"]
                    for e in range(0,len(sage_coa1)):

                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_customer_write_off1[i].get("Exclusive",0.0))
                                transactionlinedebit["TaxAmount"]=0
                                
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                    
                    transactionlinedebit["TransType"] = 2
                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']

                    transactionlinedebit["TaxGroupId"] = tax_grp_id


                    QuerySet1["Transactions"].append(transactionlinedebit)


                    payload = json.dumps(QuerySet1)
                
                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer_write_off,
                            _id, job_id, task_id, sage_customer_write_off1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
