import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio

from decimal import Decimal, ROUND_HALF_UP

from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config
from apps.home.data_util import get_job_details, add_job_status
import time
from datetime import datetime

def add_customer_ageing_type(job_id, task_id):
    logging = log_config(job_id)
    print("inside add sage invoice ============")
    try:
        logging.info(f"{job_id} inside add_sage_invoice")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        
        sage_invoice_paymnet = dbname['sage_invoice_payment']

        x = sage_invoice_paymnet.find({"job_id": job_id})
        sage_invoice_payment1 = []
        for k in x:
            sage_invoice_payment1.append(k)


        
        sage_customer_ageing_data = dbname['sage_customer_ageing']

        x = sage_customer_ageing_data.find({"job_id": job_id,"is_pushed":0})
        sage_customer_ageing_data1 = []
        for k in x:
            sage_customer_ageing_data1.append(k)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)

        sage_item = dbname['sage_item']

        x = sage_item.find({"job_id": job_id})
        sage_item1 = []
        for k in x:
            sage_item1.append(k)
        

        reckon_customer = dbname['reckon_customer']
        x = reckon_customer.find({"job_id": job_id})
        reckon_customer1 = []
        for k in x:
            reckon_customer1.append(k)

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

        sage_bank = dbname['sage_bank']
        x = sage_bank.find({"job_id": job_id})
        sage_bank1 = []
        for k in x:
            sage_bank1.append(k)

        reckon_bank_accounts= dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank1 = []
        for k in reckon_bank_accounts:
            reckon_bank1.append(k)

        
        for i in range(0, len(sage_customer_ageing_data1)):
            print(i,"no of records")
            for j in range(0,len(sage_customer_ageing_data1[i]["AgeingTransactions"])):
                # if sage_customer_ageing_data1[i]["Total"]== 0.004:

                if sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 2:

                    if sage_customer_ageing_data1[i]["AgeingTransactions"][j]["Total"] >0:

                        _id = sage_customer_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["InvoiceDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                        QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["InvoiceAmount"]=round(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        QuerySet1["InvoiceTax"]=0
                        
                        reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["InvoiceNumber"]=reference_number[0:50]
                        
                

                
                        QuerySet1["AmountTaxStatus"] = 2
                


                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                print("inside customer data=======")

                                QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                                break
                            else:
                                QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                        
                        LineItems2 = {}
                        LineItems2["TaxAmount"]=0
                        LineItems2["AmountExTax"]=round(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'],2)
                        LineItems2["Amount"]=round(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'],2)
                        LineItems2['TaxIsModified']=True
                        LineItems2["Quantity"]=1

                        tax_grp_id = {}
                
                        for m in range(0, len(taxcode_reckon)):
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        
                        LineItems2["TaxGroupId"] = tax_grp_id

                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]=="Sales":
                                LineItems2['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                        QuerySet1["LineItems"].append(LineItems2)


                        payload = json.dumps(QuerySet1)
                        print(payload,"payload data===========")
                        
                        url_invoice = f"{base_url}/invoices"

                        asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        
                    elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["Total"] <0:
                        _id = sage_customer_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["CreditNoteDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                        QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        QuerySet1["Tax"]=0
                        
                        reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["CreditNoteNumber"]=reference_number[0:50]
                        
                        QuerySet1["AmountTaxStatus"] = 2
                
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                print("inside customer data=======")

                                QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                                break
                            else:
                                QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                        
                        LineItems2 = {}
                        LineItems2["TaxAmount"]=0
                        LineItems2["AmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                        LineItems2["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                        LineItems2['TaxIsModified']=True
                        LineItems2["Quantity"]=1
                        LineItems2["LineNo"]=1

                        LineItems2["InvoiceDiscountedAmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                
                        LineItems2["InvoiceDiscountedTaxAmount"]= 0

                        tax_grp_id = {}
                
                        for m in range(0, len(taxcode_reckon)):
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        
                        LineItems2["TaxGroupId"] = tax_grp_id

                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]=="Sales":
                                LineItems2['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                        QuerySet1["LineItems"].append(LineItems2)


                        payload = json.dumps(QuerySet1)
                        print(payload,"payload data opning data negative ===========")
                        
                        url_invoice = f"{base_url}/creditnotes"

                        asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                            


                        
                    
                        
                elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 9:

                    _id = sage_customer_ageing_data1[i]["_id"]
                    QuerySet1 = {"Transactions": []}
                    QuerySet1["JournalDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                    QuerySet1["JournalStatus"]=2
                    QuerySet1["JournalNumber"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["Summary"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["AmountTaxStatus"]=3

                    
                    if sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")> 0:
                        transactionlinedebit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Sales":
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None


                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)

                        transactionlinecredit={}
                        
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                transactionlinecredit["ContactId"]=reckon_customer1[z]["ContactId"]

                        for e in range(0,len(sage_coa1)):
                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinecredit["Credit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None


                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)



                        payload = json.dumps(QuerySet1)

                    elif sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")< 0:
                        transactionlinecredit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Sales":
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                    
                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)


                        transactionlinedebit={}

                        
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                transactionlinedebit["ContactId"]=reckon_customer1[m]["ContactId"]
                        
                        for e in range(0,len(sage_coa1)):

                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinedebit["Debit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None

                        
                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)


                        payload = json.dumps(QuerySet1)
                    print(payload,"payload data ======================")
                    url = f"{base_url}/journals"

                    asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer_ageing_data,
                                _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))

                elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 4:

                    if sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")< 0:
                        _id = sage_customer_ageing_data1[i]["_id"]
                        BankAccountId={}
                        ContactId={}
                        QuerySet1={}
                        AccountsReceivableCategoryId={}
                        QuerySet1["TransDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",None))
                        QuerySet1["Reference"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    
                        for k in range(0,len(reckon_customer1)):
                                if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[k]["Description"].lower().strip():
                                    ContactId=reckon_customer1[k]["ContactId"]
                                    break

                        inv_payment_num = dbname["sage_invoice_payment"].find_one({"job_id": job_id, "DocumentNumber": sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentNumber"]})

                        if inv_payment_num !=None:
                            Sage_bankaccountid = inv_payment_num.get("BankAccountId")
                            for a in range(0,len(sage_bank1)):
                                if Sage_bankaccountid == sage_bank1[a]["ID"]:
                                    for b in range(0,len(reckon_bank1)):
                                        if sage_bank1[a]["Name"].lower().strip()==reckon_bank1[b]["Description"].lower().strip():
                                            BankAccountId=reckon_bank1[b]["BankAccountID"]
                                            break
                                        else:
                                            BankAccountId="00000000-0000-0000-0000-000000000000"


                        AccountsReceivable = None
                        for j11 in range(0,len(reckon_coa1)):
                            if reckon_coa1[j11]['Name'] == "Accounts Receivable":
                                AccountsReceivable=reckon_coa1[j11]["Id"]
                                break

                        QuerySet1["AccountsReceivableCategoryId"]=AccountsReceivable
                        QuerySet1["BankAccountId"]=BankAccountId
                        QuerySet1["ContactId"]=ContactId
                    
                        payload = json.dumps(QuerySet1)

                        print(payload,"payload data=======112222")

                        url_rcp = f"{base_url}/receipts"

                        asyncio.run(post_data_in_reckon(url_rcp, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        
                    elif sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")> 0:
                        _id = sage_customer_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["InvoiceDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                        QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["InvoiceAmount"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")
                        QuerySet1["InvoiceTax"]=0
                        reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["InvoiceNumber"]=reference_number[0:50]                
                        QuerySet1["AmountTaxStatus"] = 2
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                                break
                            else:
                                QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                        LineItems2 = {}
                        LineItems2["TaxAmount"]=0
                        LineItems2["AmountExTax"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total']
                        LineItems2["Amount"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total']
                        LineItems2['TaxIsModified']=True
                        LineItems2["Quantity"]=1
                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon)):
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        LineItems2["TaxGroupId"] = tax_grp_id
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]=="Sales":
                                LineItems2['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                        QuerySet1["LineItems"].append(LineItems2)
                        payload = json.dumps(QuerySet1)
                        print(payload,"payload data===========")
                        url_invoice = f"{base_url}/invoices"
                        asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        

                    
                        
                elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 3:
                    _id = sage_customer_ageing_data1[i]["_id"]
                    QuerySet1 = {"LineItems": []}
                    QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                    QuerySet1["CreditNoteDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                    QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                    QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                    QuerySet1["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                    QuerySet1["Tax"]=0
                    
                    reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                    QuerySet1["Reference"]=reference_number[0:50]
                    QuerySet1["CreditNoteNumber"]=reference_number[0:50]
                    
                    QuerySet1["AmountTaxStatus"] = 2
            
                    for z in range(0,len(reckon_customer1)):
                        if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                            print("inside customer data=======")

                            QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                            break
                        else:
                            QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                    
                    LineItems2 = {}
                    LineItems2["TaxAmount"]=0
                    LineItems2["AmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                    LineItems2["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                    LineItems2['TaxIsModified']=True
                    LineItems2["Quantity"]=1
                    LineItems2["LineNo"]=1

                    LineItems2["InvoiceDiscountedAmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
            
                    LineItems2["InvoiceDiscountedTaxAmount"]= 0

                    tax_grp_id = {}
            
                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            break
                    
                    LineItems2["TaxGroupId"] = tax_grp_id

                    for n in range(0,len(reckon_coa1)):
                        if reckon_coa1[n]["Name"]=="Sales":
                            LineItems2['AccountId']=reckon_coa1[n]["Id"]
                            break
                        else:
                            LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                    QuerySet1["LineItems"].append(LineItems2)


                    payload = json.dumps(QuerySet1)
                    print(payload,"payload data opning data negative ===========")
                    
                    url_invoice = f"{base_url}/creditnotes"

                    asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        

                    

                elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 0:

                    if sage_customer_ageing_data1[i]["Total"] < 0: 
                        _id = sage_customer_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["CreditNoteDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                        QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        QuerySet1["Tax"]=0
                        
                        reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["CreditNoteNumber"]=reference_number[0:50]
                        
                        QuerySet1["AmountTaxStatus"] = 2
                
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                print("inside customer data=======")

                                QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                                break
                            else:
                                QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                        
                        LineItems2 = {}
                        LineItems2["TaxAmount"]=0
                        LineItems2["AmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                        LineItems2["Amount"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                        LineItems2['TaxIsModified']=True
                        LineItems2["Quantity"]=1
                        LineItems2["LineNo"]=1

                        LineItems2["InvoiceDiscountedAmountExTax"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total'])
                
                        LineItems2["InvoiceDiscountedTaxAmount"]= 0

                        tax_grp_id = {}
                
                        for m in range(0, len(taxcode_reckon)):
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        
                        LineItems2["TaxGroupId"] = tax_grp_id

                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]=="Sales":
                                LineItems2['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                        QuerySet1["LineItems"].append(LineItems2)


                        payload = json.dumps(QuerySet1)
                        print(payload,"payload data opning data negative ===========")
                        
                        url_invoice = f"{base_url}/creditnotes"

                        asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        
                    elif sage_customer_ageing_data1[i]["Total"] > 0:

                        _id = sage_customer_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["InvoiceDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)[0:999]
                        QuerySet1["PaymentDetails"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["InvoiceAmount"]=(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        QuerySet1["InvoiceTax"]=0
                        
                        reference_number=str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["InvoiceNumber"]=reference_number[0:50]
                        
                        QuerySet1["AmountTaxStatus"] = 2
                
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                print("inside customer data=======")

                                QuerySet1["CustomerId"]=reckon_customer1[z]["ContactId"]
                                break
                            else:
                                QuerySet1["CustomerId"]= "00000000-0000-0000-0000-000000000000"

                        
                        LineItems2 = {}
                        LineItems2["TaxAmount"]=0
                        LineItems2["AmountExTax"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total']
                        LineItems2["Amount"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j]['Total']
                        LineItems2['TaxIsModified']=True
                        LineItems2["Quantity"]=1

                        tax_grp_id = {}
                
                        for m in range(0, len(taxcode_reckon)):
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        
                        LineItems2["TaxGroupId"] = tax_grp_id

                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]=="Sales":
                                LineItems2['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems2['AccountId']="00000000-0000-0000-0000-000000000000"

                        QuerySet1["LineItems"].append(LineItems2)


                        payload = json.dumps(QuerySet1)
                        print(payload,"payload data opening balance ===========")
                        
                        url_invoice = f"{base_url}/invoices"

                        asyncio.run(post_data_in_reckon(url_invoice, post_headers, payload, sage_customer_ageing_data,
                                    _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))
                        

                elif sage_customer_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 5:

                    _id = sage_customer_ageing_data1[i]["_id"]
                    QuerySet1 = {"Transactions": []}
                    QuerySet1["JournalDate"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                    QuerySet1["JournalStatus"]=2
                    QuerySet1["JournalNumber"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["Summary"]=sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["AmountTaxStatus"]=3

                    
                    if sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")> 0:
                        transactionlinedebit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Bad Debts":
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None


                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)

                        transactionlinecredit={}
                        
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                transactionlinecredit["ContactId"]=reckon_customer1[z]["ContactId"]

                        for e in range(0,len(sage_coa1)):
                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinecredit["Credit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None


                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)



                        payload = json.dumps(QuerySet1)

                    elif sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total")< 0:
                        transactionlinecredit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Bad Debts":
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                    
                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)


                        transactionlinedebit={}

                        
                        for z in range(0,len(reckon_customer1)):
                            if sage_customer_ageing_data1[i]["Customer"]["Name"].lower().strip() == reckon_customer1[z]["Description"].lower().strip():
                                transactionlinedebit["ContactId"]=reckon_customer1[m]["ContactId"]
                        
                        for e in range(0,len(sage_coa1)):

                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Receivable":
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinedebit["Debit"]=abs(sage_customer_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None

                        
                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)


                        payload = json.dumps(QuerySet1)
                    print(payload,"payload data ======================")
                    url = f"{base_url}/journals"

                    asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_customer_ageing_data,
                                _id, job_id, task_id, sage_customer_ageing_data[i]["Total"]))



    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)