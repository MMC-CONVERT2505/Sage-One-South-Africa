import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_journal_as_a_customer_adjustment(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_journal_as_a_customer_adjustment")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/journals"

        sage_customer_adjustment = dbname['sage_customer_adjustment']

        x = sage_customer_adjustment.find({"job_id": job_id})
        sage_customer_adjustment1 = []
        for k in x:
            sage_customer_adjustment1.append(k)

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

        for i in range(0, len(sage_customer_adjustment1)):
            logging.info(f"{job_id} inside sage journal data")
            _id = sage_customer_adjustment1[i]["_id"]
            QuerySet1 = {"Transactions": []}
            QuerySet1["JournalDate"]=sage_customer_adjustment1[i].get("Date",None)
            QuerySet1["JournalStatus"]=2
            QuerySet1["JournalNumber"]=sage_customer_adjustment1[i].get("DocumentNumber",None)
            QuerySet1["FullDescription"]=sage_customer_adjustment1[i].get("Description",None)
            QuerySet1["Summary"]=sage_customer_adjustment1[i].get("Reference",None)
            QuerySet1["AmountTaxStatus"]=3

            
            if sage_customer_adjustment1[i].get("Effect")==1:
                transactionlinedebit={}
                transactionlinecredit={}
                for p in range(0,len(sage_coa1)):
                    if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[p]["ID"]:
                        for n in range(0,len(reckon_coa1)):
                            if sage_coa1[p]["Name"].lower() == reckon_coa1[n]["Name"].lower():
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinedebit["Debit"]=sage_customer_adjustment1[i].get("Debit",0.0)
                                transactionlinedebit["TaxAmount"]=sage_customer_adjustment1[i].get("Tax",0.0)
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                tax_grp_id = None
             
                for m in range(0, len(taxcode_reckon)):
                    if sage_customer_adjustment1[i]["TaxTypeId"] == 0:
                        if taxcode_reckon[m]["Name"] == 'NTD':
                            tax_grp_id = taxcode_reckon[m]['ID']
                        
                        
                            break
                    elif sage_customer_adjustment1[i]["TaxTypeId"] == 443988:
                        if taxcode_reckon[m]["Name"] == 'GST':
                            tax_grp_id = taxcode_reckon[m]['ID']
                          
                            break
                    elif sage_customer_adjustment1[i]["TaxTypeId"] == 443989:
                        if taxcode_reckon[m]["Name"] == 'FRE':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            break

                transactionlinedebit["TaxGroupId"] = tax_grp_id

                transactionlinedebit["TransType"] = 2

                QuerySet1["Transactions"].append(transactionlinedebit)

                for j in range(0, len(taxcode_reckon)):
                    if taxcode_reckon[j]["Name"] == 'NTD':
                        transactionlinecredit["TaxGroupId"] = taxcode_reckon[j]['ID']


                transactionlinecredit["TransType"] = 2

                for q in range(0,len(sage_coa1)):
                    if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[q]["ID"]:
                        for o in range(0,len(reckon_coa1)):
                            if sage_coa1[q]["Name"].lower() == reckon_coa1[o]["Name"].lower():
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[o]["Id"]
                                transactionlinecredit["Credit"]=sage_customer_adjustment1[i].get("Total",0.0)
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                QuerySet1["Transactions"].append(transactionlinecredit)
          
                payload = json.dumps(QuerySet1)

            elif sage_customer_adjustment1[i].get("Effect")==2:

                transactionlinedebit={}
                transactionlinecredit={}
                for e in range(0,len(sage_coa1)):
                    if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[e]["ID"]:
                        for v in range(0,len(reckon_coa1)):
                            if sage_coa1[e]["Name"].lower() == reckon_coa1[v]["Name"].lower():
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Credit"]=sage_customer_adjustment1[i].get("Credit",0.0)
                                transactionlinedebit["TaxAmount"]=sage_customer_adjustment1[i].get("Tax",0.0)
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                tax_grp_id = None
             
                for w in range(0, len(taxcode_reckon)):
                    if sage_customer_adjustment1[i]["TaxTypeId"] == 0:
                        if taxcode_reckon[w]["Name"] == 'NTD':
                            tax_grp_id = taxcode_reckon[w]['ID']
                        
                        
                            break
                    elif sage_customer_adjustment1[i]["TaxTypeId"] == 443988:
                        if taxcode_reckon[w]["Name"] == 'GST':
                            tax_grp_id = taxcode_reckon[w]['ID']
                          
                            break
                    elif sage_customer_adjustment1[i]["TaxTypeId"] == 443989:
                        if taxcode_reckon[w]["Name"] == 'FRE':
                            tax_grp_id = taxcode_reckon[w]['ID']
                            break

                transactionlinedebit["TaxGroupId"] = tax_grp_id

                transactionlinedebit["TransType"] = 2

                QuerySet1["Transactions"].append(transactionlinedebit)

                for s in range(0, len(taxcode_reckon)):
                    if taxcode_reckon[s]["Name"] == 'NTD':
                        transactionlinecredit["TaxGroupId"] = taxcode_reckon[s]['ID']


                transactionlinecredit["TransType"] = 2

                for c in range(0,len(sage_coa1)):
                    if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[c]["ID"]:
                        for l in range(0,len(reckon_coa1)):
                            if sage_coa1[c]["Name"].lower() == reckon_coa1[l]["Name"].lower():
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[l]["Id"]
                                transactionlinecredit["Debit"]=sage_customer_adjustment1[i].get("Total",0.0)
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                QuerySet1["Transactions"].append(transactionlinecredit)
          
                payload = json.dumps(QuerySet1)



            # asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_manual_journal,
            #             _id, job_id, task_id, sage_journal1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
