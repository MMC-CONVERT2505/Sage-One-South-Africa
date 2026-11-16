import json
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
from apps.home.data_util import get_job_details
import asyncio
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

        x = sage_customer_adjustment.find({"job_id": job_id,"is_pushed":0})
        sage_customer_adjustment1 = []
        for k in x:
            sage_customer_adjustment1.append(k)

        
        reckon_customer = dbname['reckon_customer']
        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)


        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

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


        for i in range(0, len(sage_customer_adjustment1)):

            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_customer_adjustment1[i]["Date"] and end_date >= sage_customer_adjustment1[i]["Date"]:
            
                logging.info(f"{job_id} inside sage journal data")
                _id = sage_customer_adjustment1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_customer_adjustment1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                QuerySet1["JournalNumber"]=sage_customer_adjustment1[i].get("DocumentNumber",None)
                QuerySet1["FullDescription"]=sage_customer_adjustment1[i].get("Description",None)
                QuerySet1["Summary"]=sage_customer_adjustment1[i].get("DocumentNumber",None)
                QuerySet1["AmountTaxStatus"]=3
                
                if sage_customer_adjustment1[i].get("Total")< 0:
                    transactionlinedebit={}
                    for p in range(0,len(sage_coa1)):
                        if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[p]["ID"]:
                            for n in range(0,len(reckon_coa1)):
                                if sage_coa1[p]["Name"].lower() == reckon_coa1[n]["Name"].lower():
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                    transactionlinedebit["Debit"]=abs(sage_customer_adjustment1[i].get("Exclusive",0.0))
                                    transactionlinedebit["TaxAmount"]=abs(sage_customer_adjustment1[i].get("Tax",0.0))
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None
                    
                    tax_grp_id = {}                            
                    for t in range(0,len(sage_tax)):
                        for m in range(0, len(taxcode_reckon)):
                            if sage_customer_adjustment1[i]['Tax'] == 0:
                                if sage_tax[t]["Name"] == "No Tax":
                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                        tax_grp_id = taxcode_reckon[m]['ID']
                                        break
                                    
                            elif "TaxTypeId" in sage_customer_adjustment1[i]:
                                
                                if sage_customer_adjustment1[i]["TaxTypeId"]==0:
                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break

                                elif sage_customer_adjustment1[i]["TaxTypeId"] == sage_tax[t]["ID"]:
                                    if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]:  
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Manual Tax":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "No Tax":
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "GST 0%":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                        if taxcode_reckon[m]["Name"] == 'INP':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break     
                            else:
                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    tax_grp_id = taxcode_reckon[m]['ID']
                            
                            transactionlinedebit["TaxGroupId"] = tax_grp_id

                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)

                    transactionlinecredit={}
                    for p in range(0,len(sage_customer1)):
                        for m in range(0,len(reckon_customer1)):
                            if sage_customer_adjustment1[i].get("CustomerId") == sage_customer1 [p]["ID"]:
                                if sage_customer1 [p]["Name"].lower() ==  reckon_customer1[m]["FirstNameBranchName"].lower():
                                    transactionlinecredit["ContactId"]=reckon_customer1[m]["ContactId"]
                    for e in range(0,len(sage_coa1)):
                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_customer_adjustment1[i].get("Exclusive",0.0))
                                transactionlinecredit["TaxAmount"]=abs(sage_customer_adjustment1[i].get("Tax",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                    tax_grp_id = {}
                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            break
                            
                            
                        transactionlinecredit["TaxGroupId"] = tax_grp_id

                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)
                    payload = json.dumps(QuerySet1)

                elif sage_customer_adjustment1[i].get("Total")> 0:
                    transactionlinecredit={}
                    for p in range(0,len(sage_coa1)):
                        if sage_customer_adjustment1[i].get("ContraAccountId") == sage_coa1[p]["ID"]:
                            for n in range(0,len(reckon_coa1)):
                                if sage_coa1[p]["Name"].lower() == reckon_coa1[n]["Name"].lower():
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                    transactionlinecredit["Credit"]=abs(sage_customer_adjustment1[i].get("Exclusive",0.0))
                                    transactionlinecredit["TaxAmount"]=abs(sage_customer_adjustment1[i].get("Tax",0.0))
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None

                    
                    tax_grp_id = {}
                            
                    for t in range(0,len(sage_tax)):
                        for m in range(0, len(taxcode_reckon)):
                            if sage_customer_adjustment1[i]['Tax'] == 0:
                                if sage_tax[t]["Name"] == "No Tax":
                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                        tax_grp_id = taxcode_reckon[m]['ID']
                                        break
                                    
                            elif "TaxTypeId" in sage_customer_adjustment1[i]:
                                
                                if sage_customer_adjustment1[i]["TaxTypeId"]==0:
                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break

                                elif sage_customer_adjustment1[i]["TaxTypeId"] == sage_tax[t]["ID"]:
                                    if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]:  
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Manual Tax":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "No Tax":
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "GST 0%":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                        if taxcode_reckon[m]["Name"] == 'INP':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                        
                                    elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    
                                    elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                        if taxcode_reckon[m]["Name"] == 'GST':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break     
                                    

                            else:
                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    tax_grp_id = taxcode_reckon[m]['ID']
                            
                            transactionlinecredit["TaxGroupId"] = tax_grp_id

                    transactionlinecredit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinecredit)


                    transactionlinedebit={}

                    
                    for p in range(0,len(sage_customer1)):
                        for m in range(0,len(reckon_customer1)):
                            if sage_customer_adjustment1[i].get("CustomerId") == sage_customer1 [p]["ID"]:
                                if sage_customer1 [p]["Name"].lower() ==  reckon_customer1[m]["FirstNameBranchName"].lower():
                                    transactionlinedebit["ContactId"]=reckon_customer1[m]["ContactId"]
                    for e in range(0,len(sage_coa1)):

                        for v in range(0,len(reckon_coa1)):
                            if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_customer_adjustment1[i].get("Total",0.0))
                                transactionlinedebit["TaxAmount"]=0
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None

                    
                    tax_grp_id = {}
                            
                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            break
                        
                            
                        transactionlinedebit["TaxGroupId"] = tax_grp_id

                    transactionlinedebit["TransType"] = 2

                    QuerySet1["Transactions"].append(transactionlinedebit)


                    payload = json.dumps(QuerySet1)
            
                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer_adjustment,
                            _id, job_id, task_id, sage_customer_adjustment1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
