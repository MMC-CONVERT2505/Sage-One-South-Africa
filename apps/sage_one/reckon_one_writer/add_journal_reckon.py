import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.home.data_util import get_job_details, add_job_status
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_journal_reckon(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_journal_reckon")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/journals"

        sage_journal = dbname['sage_manual_journal']

        x = sage_journal.find({"job_id": job_id,"is_pushed":0})
        sage_journal1 = []
        for k in x:
            sage_journal1.append(k)

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

        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

        def get_account_type(value):
            account_type = None
            if value == 1:
                account_type = 'Sales'
            elif value == 2:
                account_type = 'Cost of Sales'
            elif value == 3:
                account_type = 'Other Income'
            elif value == 4:
                account_type = 'Expenses'
            elif value == 5:
                account_type = 'Non-Current Assets'
            elif value == 6:
                account_type = 'Current Assets'
            elif value == 7:
                account_type = 'Non-Current Liabilities'
            elif value == 8:
                account_type = 'Current Liabilities'
            elif value == 9:
                account_type = 'Owners Equity'
            elif value == 10:
                account_type = 'Income Tax'

            logging.info(f"account type-->{account_type}")

            return account_type

        def get_account_type_id(value):
            account_type_id = None
            if value == 1:
                account_type_id = 1
            elif value == 8:
                account_type_id = 4
            elif value == 4:
                account_type_id = 2
            elif value == 5:
                account_type_id = 12
            elif value == 7:
                account_type_id = 16
            elif value == 9:
                account_type_id = 5
            elif value == 3:
                account_type_id = 6
            elif value == 6:
                account_type_id = 3
            elif value == 2:
                account_type_id = 8
            elif value == 10:
                account_type_id = 2

            logging.info(f"{job_id} account_type_id-->{account_type_id}")
            return account_type_id
        
        for i in range(0, len(sage_journal1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_journal1[i]["Date"] and end_date >= sage_journal1[i]["Date"]:
            
                print(sage_journal1[i])
                logging.info(f"{job_id} inside sage journal data")
                _id = sage_journal1[i]["_id"]
                QuerySet1 = {"Transactions": []}
                QuerySet1["JournalDate"]=sage_journal1[i].get("Date",None)
                QuerySet1["JournalStatus"]=2
                if sage_journal1[i]["Reference"] !=  None and  sage_journal1[i]["Reference"] !="":
                    QuerySet1["Summary"]=sage_journal1[i].get("Reference",None)
                else:
                    QuerySet1["Summary"]=sage_journal1[i].get("ID",None)
                QuerySet1["JournalNumber"]=sage_journal1[i].get("Reference",None)
                QuerySet1["AmountTaxStatus"]=3





                
                if sage_journal1[i].get("Effect")==1:
                    print("effect = 1")
                    transactionlinedebit={}
                    transactionlinecredit={}
                    for p in range(0,len(sage_coa1)):
                        if sage_journal1[i].get("AccountId") == sage_coa1[p]["ID"]:
                            for n in range(0,len(reckon_coa1)):
                                if sage_coa1[p]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                    # DebitAmount=abs(sage_journal1[i].get("Debit",0.0)+sage_journal1[i].get("Tax",0.0))
                                    transactionlinedebit["Debit"]=round(abs(sage_journal1[i].get("Exclusive",0.0)),2)
                                    transactionlinedebit["TaxAmount"]=round(abs(sage_journal1[i].get("Tax",0.0)),2)
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None

                    tax_grp_id = {}
                    for i1 in range(0, len(sage_coa1)):
                        if sage_journal1[i]['AccountId'] == sage_coa1[i1]['ID']:
                            print("match coa===========")

                            Accounttype_data = get_account_type(
                                sage_coa1[i1]["Category"]["ID"]),
                            single_element = Accounttype_data[0]
                            QuerySet1["TYPE"] = single_element

                            QuerySet1["AccountType"] = get_account_type_id(
                                sage_coa1[i1]["Category"]["ID"])
                            QuerySet1["AccountCode"] = sage_coa1[i1]["ID"]
                        
                            for t in range(0,len(sage_tax)):
                                for m in range(0, len(taxcode_reckon)):
                                    if sage_journal1[i]['Tax'] == 0:
                                        if sage_tax[t]["Name"] == "No Tax":
                                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    transactionlinedebit["TransType"] = 1
                                                    break
                                            else:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    transactionlinedebit["TransType"] = 2
                                                    break


                                    if "TaxTypeId" in sage_journal1[i]:

                                        if sage_journal1[i]["TaxTypeId"] == sage_tax[t]["ID"]:

                                            if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]: 
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1

                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break
                                            elif sage_tax[t]["Name"] == "Manual Tax":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break
                                            

                                            elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "GST 0%":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'INP':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCI':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'CAG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-Capital Purchase inc GST"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "No Tax":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        break


                                        # else:
                                        #     if taxcode_reckon[m]["Name"] == 'NO TAX':
                                        #         tax_grp_id = taxcode_reckon[m]['ID']
                                        #         continue
                                               
                                        
                                
                                    else:
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']

                                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                transactionlinedebit["TransType"] = 1
                                            else:
                                                transactionlinedebit["TransType"] = 2
                                            break
            
                                            
                                        
                    transactionlinedebit["TaxGroupId"] = tax_grp_id

                    transactionlinedebit["TaxModified"]=True

                 
                    QuerySet1["Transactions"].append(transactionlinedebit)

                    for j in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[j]["Name"] == 'NO TAX':
                            transactionlinecredit["TaxGroupId"] = taxcode_reckon[j]['ID']
                            


                    for q in range(0,len(sage_coa1)):
                        if sage_journal1[i].get("ContraAccountId") == sage_coa1[q]["ID"]:

                            Accounttype_data = get_account_type(
                                sage_coa1[q]["Category"]["ID"]),
                            single_element = Accounttype_data[0]
                            QuerySet1["TYPE"] = single_element

                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                transactionlinecredit["TransType"] = 1
                            else:
                                transactionlinecredit["TransType"] = 2

                            for o in range(0,len(reckon_coa1)):
                                if sage_coa1[q]["Name"].lower().strip().replace(":", " ") == reckon_coa1[o]["Name"].lower().strip().replace(":", " "):
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[o]["Id"]
                                    transactionlinecredit["Credit"]=round(abs(sage_journal1[i].get("Total",0.0)),2)
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None
                                
                                transactionlinecredit["TaxModified"]=True

                    QuerySet1["Transactions"].append(transactionlinecredit)
            
                    payload = json.dumps(QuerySet1)
                    print(payload,"payload data=============")

                elif sage_journal1[i].get("Effect")==2:
                    print("effect = 2")
                    tax_grp_id={}
                    transactionlinedebit={}
                    transactionlinecredit={}
                    for e in range(0,len(sage_coa1)):
                        if sage_journal1[i].get("AccountId") == sage_coa1[e]["ID"]:
                            for v in range(0,len(reckon_coa1)):
                                if sage_coa1[e]["Name"].lower().strip().replace(":", " ") == reckon_coa1[v]["Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    # CreditAmount=round(abs(sage_journal1[i].get("Credit",0.0)+sage_journal1[i].get("Tax",0.0)),4)
                                    transactionlinedebit["Credit"]=round(abs(sage_journal1[i].get("Exclusive",0.0)),2)
                                    transactionlinedebit["TaxAmount"]=round(abs(sage_journal1[i].get("Tax",0.0)),2)
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None

                    tax_grp_id = {}
                    for i1 in range(0, len(sage_coa1)):
                        if sage_journal1[i]['AccountId'] == sage_coa1[i1]['ID']:

                            Accounttype_data = get_account_type(
                                sage_coa1[i1]["Category"]["ID"]),
                            single_element = Accounttype_data[0]
                            QuerySet1["TYPE"] = single_element
                            QuerySet1["AccountType"] = get_account_type_id(
                                sage_coa1[i1]["Category"]["ID"])
                            QuerySet1["AccountCode"] = sage_coa1[i1]["ID"]
                            

                        
                            for t in range(0,len(sage_tax)):
                                for m in range(0, len(taxcode_reckon)):
                                    if sage_journal1[i]['Tax'] == 0:
                                        if sage_tax[t]["Name"] == "No Tax":
                                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    transactionlinedebit["TransType"] = 1
                                                    break
                                            else:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    transactionlinedebit["TransType"] = 2
                                                    break


                                    if "TaxTypeId" in sage_journal1[i]:
                                        if sage_journal1[i]["TaxTypeId"] == sage_tax[t]["ID"]:
                                            if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]: 
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1

                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break
                                            elif sage_tax[t]["Name"] == "Manual Tax":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break
                                            
                                            elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "GST 0%":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'INP':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCI':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'CAG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'FRE':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCF':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break

                                            elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                                if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'GST':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 1
                                                        break
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NCG':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        transactionlinedebit["TransType"] = 2
                                                        break
                                       

                                    else:
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']

                                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                transactionlinedebit["TransType"] = 1
                                            else:
                                                transactionlinedebit["TransType"] = 2
                                            break
                    
                    transactionlinedebit["TaxModified"]=True
                    transactionlinedebit["TaxGroupId"] = tax_grp_id

                    QuerySet1["Transactions"].append(transactionlinedebit)



                    for j in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[j]["Name"] == 'NO TAX':
                            transactionlinecredit["TaxGroupId"] = taxcode_reckon[j]['ID']


                    for c in range(0,len(sage_coa1)):
                        if sage_journal1[i].get("ContraAccountId") == sage_coa1[c]["ID"]:


                            Accounttype_data = get_account_type(
                                sage_coa1[c]["Category"]["ID"]),
                            single_element = Accounttype_data[0]
                            QuerySet1["TYPE"] = single_element

                            if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                transactionlinecredit["TransType"] = 1
                            else:
                                transactionlinecredit["TransType"] = 2


                            for l in range(0,len(reckon_coa1)):
                                if sage_coa1[c]["Name"].lower().strip().replace(":", " ") == reckon_coa1[l]["Name"].lower().strip().replace(":", " "):
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[l]["Id"]
                                    transactionlinecredit["Debit"]=round(abs(sage_journal1[i].get("Total",0.0)),2)
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None
                                transactionlinecredit["TaxModified"]=True
                    QuerySet1["Transactions"].append(transactionlinecredit)
            
                payload = json.dumps(QuerySet1)

                print(payload)
                print("-------------------------------------")
                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_journal,
                            _id, job_id, task_id, sage_journal1[i]["ID"]))
            # else:
            #     _id = sage_journal1[i]["_id"]
            #     sage_journal.update_one({'_id': _id}, {"$set": {"payload":"Out of date"}}, upsert=True)
            
            #     print("out of date")
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)