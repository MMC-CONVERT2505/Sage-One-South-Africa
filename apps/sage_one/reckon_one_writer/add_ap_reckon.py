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

def add_supplier_ageing_type(job_id, task_id):
    logging = log_config(job_id)
    print("inside add sage bill ============")
    try:
        logging.info(f"{job_id} inside add_sage_bill")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)
        
        sage_bill_paymnet_data = dbname['sage_bill_payment'].find({"job_id": job_id,"is_pushed":0})

        sage_bill_paymnet_data1 = []
        for k in sage_bill_paymnet_data:
            sage_bill_paymnet_data1.append(k)

        sage_supplier_ageing_data = dbname['sage_supplier_ageing']

        x1 = sage_supplier_ageing_data.find({"job_id": job_id,"is_pushed":0})
        sage_supplier_ageing_data1 = []
        for k1 in x1:
            sage_supplier_ageing_data1.append(k1)

        template1 = dbname['reckon_vendorcredit_template'].find(
            {"job_id": job_id})
        template = []
        for i in template1:
            template.append(i)


        sage_bill = dbname['sage_bill']

        x2 = sage_bill.find({"job_id": job_id,"is_pushed":0})
        sage_bill1 = []
        for k2 in x2:
            sage_bill1.append(k2)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)

        sage_bank = dbname['sage_bank']
        x01 = sage_bank.find({"job_id": job_id})
        sage_bank1 = []
        for k02 in x01:
            sage_bank1.append(k02)

        reckon_bank_accounts= dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank1 = []
        for k11 in reckon_bank_accounts:
            reckon_bank1.append(k11)

        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p11 in sage_tax1:
            sage_tax.append(p11)

        sage_item = dbname['sage_item']

        x3 = sage_item.find({"job_id": job_id})
        sage_item1 = []
        for k3 in x3:
            sage_item1.append(k3)

        reckon_supplier = dbname['reckon_supplier']
        x4 = reckon_supplier.find({"job_id": job_id})
        reckon_supplier1 = []
        for k4 in x4:
            reckon_supplier1.append(k4)

        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p1 in reckon_coa:
            reckon_coa1.append(p1)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon_data = []
        for p99 in taxcode_reckon1:
            taxcode_reckon_data.append(p99)

        reckon_item = dbname["reckon_item"].find({"job_id": job_id})
        reckon_item1 = []
        for p01 in reckon_item:
            reckon_item1.append(p01)

        templateid = None
        for t5 in range(0, len(template)):
            if template[t5]['Name'] == "Standard Supplier Adjustment Note":
                templateid = template[t5]["ID"]


        print(taxcode_reckon_data,"taxcode_reckon_data====")

       
        for i in range(0, len(sage_supplier_ageing_data1)):
            for j in range(0,len(sage_supplier_ageing_data1[i]["AgeingTransactions"])):
                # if sage_supplier_ageing_data1[i] ["Total"] == -290.87:
                if sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 102:

                    if sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["Total"] >0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["BillDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                        QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)

                        QuerySet1["BillAmount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None),2)
                        QuerySet1["BillTax"] = 0

                        if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                            reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                        else:
                            reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number_id[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                        
                        QuerySet1["AmountTaxStatus"] = 2
                    
                        for k in range(0, len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                        LineItems1 = {}
                        LineItems1['TaxIsModified']=True
                        LineItems1["LineNo"] = 1
                                    
                        LineItems1["TaxAmount"] = 0       
                        LineItems1["Amount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AccountId"] = None
                        LineItems1["InvoiceDiscountedAmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["InvoiceDiscountedTaxAmount"] = 0
                        
                        LineItems1["Quantity"] = 1

                        for n in range(0, len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]== "Purchases":
                                LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon_data)):
                            if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon_data[m]['ID']
                                break
                        
                        LineItems1["TaxGroupId"] = tax_grp_id

                        QuerySet1["LineItems"].append(LineItems1)

                        payload = json.dumps(QuerySet1)
                        print(payload,"print payload ============")

                        url = f"{base_url}/bills"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        
                    elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["Total"] < 0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["SupplierCreditNoteDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                        QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        LineItems1['ChargeableItemId'] = None
                        QuerySet1["TemplateId"] = templateid

                        QuerySet1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None))
                        QuerySet1["Tax"] = 0

                        if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                            reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number[0:50]
                            QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                        else:
                            reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number_id[0:50]
                            QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                        
                        QuerySet1["AmountTaxStatus"] = 2
                    
                        for k in range(0, len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                        LineItems1 = {}
                        LineItems1['TaxIsModified']=True
                        LineItems1["LineNo"] = 1
                                    
                        LineItems1["TaxAmount"] = 0       
                        LineItems1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["AmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["AccountId"] = None
                        LineItems1["InvoiceDiscountedAmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["InvoiceDiscountedTaxAmount"] = 0
                        
                        LineItems1["Quantity"] = 1

                        for n in range(0, len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]== "Purchases":
                                LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                LineItems1['AccountingCategoryId'] = reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon_data)):
                            if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon_data[m]['ID']
                                break
                        
                        LineItems1["TaxGroupId"] = tax_grp_id

                        QuerySet1["LineItems"].append(LineItems1)

                        payload = json.dumps(QuerySet1)
                        print(payload,"print payload vendore credite ============")

                        url = f"{base_url}/suppliercreditnotes"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        

                    
                        
                elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 104:

                    if sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["Total"] < 0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {}
                        BankAccountId={}
                        ContactId={}
                        QuerySet1["TransDate"]=sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Amount"]=abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None))
                        QuerySet1["Reference"]=sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)

                        for k in range(0,len(reckon_supplier1)):
                                if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                    ContactId=reckon_supplier1[k]["ContactId"]
                                    break

                        bill_payment_num = dbname["sage_bill_payment"].find_one({"job_id": job_id, "DocumentNumber": sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentNumber"]})

                        if bill_payment_num !=None:
                            Sage_bankaccountid = bill_payment_num.get("BankAccountId")
                            for a in range(0,len(sage_bank1)):
                                if Sage_bankaccountid == sage_bank1[a]["ID"]:
                                    for b in range(0,len(reckon_bank1)):
                                        if sage_bank1[a]["Name"].lower().strip()==reckon_bank1[b]["Description"].lower().strip():
                                            BankAccountId=reckon_bank1[b]["BankAccountID"]
                                            break
                                        else:
                                            BankAccountId="00000000-0000-0000-0000-000000000000"

                        AccountsPayable = None
                        for j11 in range(0,len(reckon_coa1)):
                            if reckon_coa1[j11]['Name'] == "Accounts Payable":
                                AccountsPayable=reckon_coa1[j11]["Id"]
                                break

                        QuerySet1["AccountsPayableCategoryId"]=AccountsPayable
                        QuerySet1["BankAccountId"]=BankAccountId
                        QuerySet1["ContactId"]=ContactId
                    
                        payload = json.dumps(QuerySet1)

                        print(payload,"payload data=======112222")

                        url = f"{base_url}/payments"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        
                    elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["Total"] > 0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["BillDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                        QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)

                        QuerySet1["BillAmount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None),2)
                        QuerySet1["BillTax"] = 0

                        if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                            reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                        else:
                            reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number_id[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                        
                        QuerySet1["AmountTaxStatus"] = 2
                    
                        for k in range(0, len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                        LineItems1 = {}
                        LineItems1['TaxIsModified']=True
                        LineItems1["LineNo"] = 1
                                    
                        LineItems1["TaxAmount"] = 0       
                        LineItems1["Amount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AccountId"] = None
                        LineItems1["InvoiceDiscountedAmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["InvoiceDiscountedTaxAmount"] = 0
                        
                        LineItems1["Quantity"] = 1

                        for n in range(0, len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]== "Purchases":
                                LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                break
                            else:
                                LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon_data)):
                            if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon_data[m]['ID']
                                break
                        
                        LineItems1["TaxGroupId"] = tax_grp_id

                        QuerySet1["LineItems"].append(LineItems1)

                        payload = json.dumps(QuerySet1)
                        print(payload,"print payload ============")

                        url = f"{base_url}/bills"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        

                    
                elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 109:
                    _id = sage_supplier_ageing_data1[i]["_id"]
                    QuerySet1 = {"Transactions": []}
                    QuerySet1["JournalDate"]=sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                    QuerySet1["JournalStatus"]=2
                    QuerySet1["JournalNumber"]=sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["Summary"]=sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber",None)
                    QuerySet1["AmountTaxStatus"]=3

                    if sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total")> 0:
                        transactionlinedebit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Purchases":
                                transactionlinedebit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinedebit["Debit"]=abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinedebit["AccountingCategoryId"]=None


                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)

                        transactionlinecredit={}
                        
                        for z in range(0,len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[z]["Description"].lower().strip():
                                transactionlinecredit["ContactId"]=reckon_supplier1[z]["ContactId"]

                        for e in range(0,len(sage_coa1)):
                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Payable":
                                    transactionlinecredit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinecredit["Credit"]=abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinecredit["AccountingCategoryId"]=None


                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)


                        payload = json.dumps(QuerySet1)

                    elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total")< 0:
                        transactionlinecredit={}
                        for n in range(0,len(reckon_coa1)):
                            if reckon_coa1[n]["Name"] == "Purchases":
                                transactionlinecredit["AccountingCategoryId"]=reckon_coa1[n]["Id"]
                                transactionlinecredit["Credit"]=abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                break
                            else:
                                transactionlinecredit["AccountingCategoryId"]=None

                    
                        transactionlinecredit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinecredit)


                        transactionlinedebit={}

                        
                        for z in range(0,len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[z]["Description"].lower().strip():
                                transactionlinedebit["ContactId"]=reckon_supplier1[z]["ContactId"]
                        
                        for e in range(0,len(sage_coa1)):

                            for v in range(0,len(reckon_coa1)):
                                if reckon_coa1[v]["Name"] == "Accounts Payable":
                                    transactionlinedebit["AccountingCategoryId"]=reckon_coa1[v]["Id"]
                                    transactionlinedebit["Debit"]=abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",0.0))
                                    break
                                else:
                                    transactionlinedebit["AccountingCategoryId"]=None

                        
                        transactionlinedebit["TransType"] = 2

                        QuerySet1["Transactions"].append(transactionlinedebit)


                        payload = json.dumps(QuerySet1)
                    print(payload,"payload data SADJ data ======================")
                    url = f"{base_url}/journals"

                    asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                    
                elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 100:
                    if sage_supplier_ageing_data1[i]["Total"] < 0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["SupplierCreditNoteDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                        QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)
                        QuerySet1["TemplateId"] = templateid

                        QuerySet1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None))
                        QuerySet1["Tax"] = 0

                        if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                            reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number[0:50]
                            QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                        else:
                            reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number_id[0:50]
                            QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                        
                        QuerySet1["AmountTaxStatus"] = 2
                    
                        for k in range(0, len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                        LineItems1 = {}
                        LineItems1['TaxIsModified']=True
                        LineItems1["LineNo"] = 1
                                    
                        LineItems1["TaxAmount"] = 0       
                        LineItems1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["AmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["AccountId"] = None
                        LineItems1["InvoiceDiscountedAmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                        LineItems1["InvoiceDiscountedTaxAmount"] = 0

                        
                        LineItems1["Quantity"] = -1

                        for n in range(0, len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]== "Purchases":
                                LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                LineItems1['AccountingCategoryId'] = reckon_coa1[n]["Id"]
                               
                                break
                            else:
                                LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon_data)):
                            if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon_data[m]['ID']
                                break
                        
                        LineItems1["TaxGroupId"] = tax_grp_id

                        QuerySet1["LineItems"].append(LineItems1)

                        payload = json.dumps(QuerySet1)
                        print(payload,"print payload ============")

                        url = f"{base_url}/suppliercreditnotes"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        
                    elif sage_supplier_ageing_data1[i]["Total"] > 0:
                        _id = sage_supplier_ageing_data1[i]["_id"]
                        QuerySet1 = {"LineItems": []}
                        QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                        QuerySet1["BillDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                        QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                        QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)

                        QuerySet1["BillAmount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None),2)
                        QuerySet1["BillTax"] = 0

                        if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                            reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                        else:
                            reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                            QuerySet1["Reference"]=reference_number_id[0:50]
                            QuerySet1["BillNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                        
                        QuerySet1["AmountTaxStatus"] = 2
                    
                        for k in range(0, len(reckon_supplier1)):
                            if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                                QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                        LineItems1 = {}
                        LineItems1['TaxIsModified']=True
                        LineItems1["LineNo"] = 1
                                    
                        LineItems1["TaxAmount"] = 0       
                        LineItems1["Amount"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["AccountId"] = None
                        LineItems1["InvoiceDiscountedAmountExTax"] = round(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"),2)
                        LineItems1["InvoiceDiscountedTaxAmount"] = 0
                        
                        LineItems1["Quantity"] = 1

                        for n in range(0, len(reckon_coa1)):
                            if reckon_coa1[n]["Name"]== "Purchases":
                                LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                               
                                break
                            else:
                                LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                        tax_grp_id = {}
                        for m in range(0, len(taxcode_reckon_data)):
                            if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon_data[m]['ID']
                                break
                        
                        LineItems1["TaxGroupId"] = tax_grp_id

                        QuerySet1["LineItems"].append(LineItems1)

                        payload = json.dumps(QuerySet1)
                        print(payload,"print payload ============")

                        url = f"{base_url}/bills"

                        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                                _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                        
                elif sage_supplier_ageing_data1[i]["AgeingTransactions"][j]["DocumentTypeId"]== 103:
                    _id = sage_supplier_ageing_data1[i]["_id"]
                    QuerySet1 = {"LineItems": []}
                    QuerySet1["DueDate"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DueDate",None)
                    QuerySet1["SupplierCreditNoteDate"] =sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Date",None)
                    QuerySet1["Notes"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Comment",None)
                    QuerySet1["PaymentDetails"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("",None)

                    QuerySet1["TemplateId"] = templateid


                    QuerySet1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total",None))
                    QuerySet1["Tax"] = 0

                    if "DocumentNumber" in sage_supplier_ageing_data1[i]["AgeingTransactions"][j]:
                        reference_number=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("DocumentNumber")
                    else:
                        reference_number_id=str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID"))+"-"+str(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Reference",None))
                        QuerySet1["Reference"]=reference_number_id[0:50]
                        QuerySet1["SupplierCreditNoteNumber"] = sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("ID")
                    
                    QuerySet1["AmountTaxStatus"] = 2
                
                    for k in range(0, len(reckon_supplier1)):
                        if sage_supplier_ageing_data1[i]["Supplier"]["Name"].lower().strip() == reckon_supplier1[k]["Description"].lower().strip():
                            QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                    LineItems1 = {}
                    LineItems1['TaxIsModified']=True
                    LineItems1["LineNo"] = 1
                                
                    LineItems1["TaxAmount"] = 0       
                    LineItems1["Amount"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                    LineItems1["AmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                    LineItems1["AccountId"] = None
                    LineItems1["InvoiceDiscountedAmountExTax"] = abs(sage_supplier_ageing_data1[i]["AgeingTransactions"][j].get("Total"))
                    LineItems1["InvoiceDiscountedTaxAmount"] = 0
                    
                    LineItems1["Quantity"] = -1

                    for n in range(0, len(reckon_coa1)):
                        if reckon_coa1[n]["Name"]== "Purchases":
                            LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                            LineItems1['AccountingCategoryId'] = reckon_coa1[n]["Id"]
                               
                            break
                        else:
                            LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"


                    tax_grp_id = {}
                    for m in range(0, len(taxcode_reckon_data)):
                        if taxcode_reckon_data[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon_data[m]['ID']
                            break
                    
                    LineItems1["TaxGroupId"] = tax_grp_id

                    QuerySet1["LineItems"].append(LineItems1)

                    payload = json.dumps(QuerySet1)
                    print(payload,"print payload ============")

                    url = f"{base_url}/suppliercreditnotes"

                    asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_supplier_ageing_data,
                            _id, job_id, task_id, sage_supplier_ageing_data1[i]["Total"]))
                    


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)