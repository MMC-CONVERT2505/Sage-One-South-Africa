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
import time
from datetime import datetime



def add_bill_in_reckon(job_id, task_id):
    logging = log_config(job_id)

    try:
        
        logging.info(f"{job_id} inside add_bill_in_reckon ")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)



        sage_bill = dbname['sage_bill']

        x = sage_bill.find({"job_id": job_id,"is_pushed":0})
        sage_bill1 = []
        for k in x:
            sage_bill1.append(k)

        sage_coa = dbname["sage_coa"].find({"job_id": job_id})
        sage_coa1 = []
        for c1 in sage_coa:
            sage_coa1.append(c1)

        
        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

        sage_item = dbname['sage_item']

        x = sage_item.find({"job_id": job_id})
        sage_item1 = []
        for k in x:
            sage_item1.append(k)

        reckon_supplier = dbname['reckon_supplier']
        x = reckon_supplier.find({"job_id": job_id})
        reckon_supplier1 = []
        for k in x:
            reckon_supplier1.append(k)

        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p1 in reckon_coa:
            reckon_coa1.append(p1)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        reckon_item = dbname["reckon_item"].find({"job_id": job_id})
        reckon_item1 = []
        for p01 in reckon_item:
            reckon_item1.append(p01)
            
        template1 = dbname['reckon_vendorcredit_template'].find(
            {"job_id": job_id})
        template = []
        for i in template1:
            template.append(i)

        templateid = None
        for t5 in range(0, len(template)):
            if template[t5]['Name'] == "Standard Supplier Adjustment Note":
                templateid = template[t5]["ID"]


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
        
        record_count = 0
        start_time = time.time()
        MAX_RECORDS_PER_MINUTE = 100
        EXTRA_WAIT_TIME = 4

        for i in range(0, len(sage_bill1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_bill1[i]["Date"] and end_date >= sage_bill1[i]["Date"]:


                current_time = time.time()

                elapsed_time = current_time - start_time
    
                if elapsed_time >= 60:
                    record_count = 0
                    start_time = current_time

                record_count += 1
                if record_count > MAX_RECORDS_PER_MINUTE:
                    time_left = 60 - elapsed_time
                    wait_time = time_left + EXTRA_WAIT_TIME
                    time.sleep(wait_time)
                    record_count = 0
                    start_time = time.time()


                logging.info(f"{job_id} inside sage invoice data")

                if sage_bill1[i].get("Total") > 0:
                    _id = sage_bill1[i]["_id"]
                    QuerySet1 = {"LineItems": []}
                    QuerySet1["DueDate"] = sage_bill1[i].get("DueDate", None)
                    QuerySet1["BillDate"] = sage_bill1[i].get("Date", None)
                    QuerySet1["Notes"] = sage_bill1[i].get("Message", None)[0:100]
                    QuerySet1["PaymentDetails"] = sage_bill1[i].get("", None)

                    QuerySet1["BillAmount"] = sage_bill1[i].get("Total")
                    QuerySet1["BillTax"] = sage_bill1[i].get("Tax")


                    if "DocumentNumber" in sage_bill1[i]:
                        reference_number=str(sage_bill1[i].get("DocumentNumber"))+"-"+str(sage_bill1[i].get("Reference",None))
                        QuerySet1["Reference"]=reference_number[0:50]
                        QuerySet1["BillNumber"] = sage_bill1[i].get("DocumentNumber")
                    else:
                        reference_number_id=str(sage_bill1[i].get("ID"))+"-"+str(sage_bill1[i].get("Reference",None))
                        QuerySet1["Reference"]=reference_number_id[0:50]
                        QuerySet1["BillNumber"] = sage_bill1[i].get("ID")
                    if sage_bill1[i].get("Inclusive") == True:

                        QuerySet1["AmountTaxStatus"] = 2
                    else:
                        QuerySet1["AmountTaxStatus"] = 3

                    for k in range(0, len(reckon_supplier1)):
                        if sage_bill1[i]["SupplierName"].lower() == reckon_supplier1[k]["Description"].lower():
                            QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]

                    total_lines = 0
                    for k in range(0, len(sage_bill1[i]['Lines'])):
                        logging.info(f"{job_id} length of sage-->bill-->lines  {len(sage_bill1[i]['Lines'][k])}")
                        LineItems1 = {}
                        total_lines += len(sage_bill1[i]['Lines'])
                        if sage_bill1[i]['Lines'][k]["LineType"] == 0:
                            LineItems1["LineNo"] = total_lines
                            LineItems1["Item"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            LineItems1['TaxIsModified']=True
                            for p in range(0, len(sage_item1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_item1[p]["ID"]:
                                    logging.info(f"{job_id} match id ")
                                    for q in range(0, len(reckon_item1)):
                                        if sage_item1[p]["Code"] == reckon_item1[q]["FullName"]:
                                            LineItems1['ChargeableItemId'] = reckon_item1[q]["Id"]
                                            LineItems1["AccountingCategoryId"] = reckon_item1[q].get(
                                                "PurchaseCategoryId", None)
                                            break
                                        else:
                                            LineItems1['ChargeableItemId'] = "00000000-0000-0000-0000-000000000000"

                                

                            if sage_bill1[i]['Lines'][k]["Total"] > 0:

                            
                                LineItems1["Amount"] = abs(sage_bill1[i]['Lines'][k]["Total"])
                                LineItems1["AmountExTax"] = abs(round(
                                sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                LineItems1["Quantity"] = sage_bill1[i]["Lines"][k].get(
                                "Quantity", 1)

                                LineItems1["TaxAmount"] = abs(sage_bill1[i]['Lines'][k]['Tax'])
                                LineItems1["InvoiceDiscountedTaxAmount"] = abs(sage_bill1[i]['Lines'][k]['Tax'])
                                if QuerySet1["AmountTaxStatus"] == 3:
                                    LineItems1["InvoiceDiscountedAmountExTax"] = abs(round(
                                        sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                
                                else:
                                    
                                    LineItems1["InvoiceDiscountedAmountExTax"] = abs(round(
                                        sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                    
                            else:
                                LineItems1["Amount"] = -(round(sage_bill1[i]['Lines'][k]["Total"],2))
                                LineItems1["AmountExTax"] = -(round(
                                sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                LineItems1["Quantity"] = sage_bill1[i]["Lines"][k].get(
                                "Quantity", 1)

                                LineItems1["TaxAmount"] = -(round(sage_bill1[i]['Lines'][k]['Tax'],2))
                                LineItems1["InvoiceDiscountedTaxAmount"] = -(round(sage_bill1[i]['Lines'][k]['Tax'],2))
                                if QuerySet1["AmountTaxStatus"] == 3:
                                    LineItems1["InvoiceDiscountedAmountExTax"] = -(round(
                                        sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                else:
                                    LineItems1["InvoiceDiscountedAmountExTax"] = -(round(
                                        sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                        
                            LineItems1["AccountId"] = None
                            LineItems1["Description"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            
                            tax_grp_id = {}
                            for t in range(0,len(sage_tax)):
                                for m in range(0, len(taxcode_reckon)):

                                    if sage_bill1[i]['Lines'][k]["TaxTypeId"] == 0:
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    

                                    elif sage_bill1[i]['Lines'][k]['TaxTypeId'] == sage_tax[t]["ID"] :
                                    
                                        if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]:
                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                break
                                            
                                        elif sage_tax[t]["Name"] == "Manual Tax":
                                            if taxcode_reckon[m]["Name"] == 'GST':
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
                                            continue
                                
                                    LineItems1["TaxGroupId"] = tax_grp_id

                            QuerySet1["LineItems"].append(LineItems1)

                        elif sage_bill1[i]['Lines'][k]["LineType"] == 1:
                            LineItems1["LineNo"] = total_lines
                            LineItems1["Description"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            LineItems1["Quantity"] = sage_bill1[i]["Lines"][k].get(
                                "Quantity", 1)
                            LineItems1["TaxAmount"] = sage_bill1[i]['Lines'][k].get(
                                'Tax', 0.0)
                            LineItems1["Amount"] = abs(round(sage_bill1[i]['Lines'][k]["Total"],2))
                            LineItems1["AmountExTax"] = abs(round(
                                sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                            LineItems1['ChargeableItemId'] = None
                            LineItems1["InvoiceDiscountedTaxAmount"] = sage_bill1[i]['Lines'][k].get(
                                'Tax', 0.0)
                            LineItems1['TaxIsModified']=True

                            if QuerySet1["AmountTaxStatus"] == 3:
                                LineItems1["InvoiceDiscountedAmountExTax"] = abs(round(
                                    sage_bill1[i]["Lines"][k]["Exclusive"], 2))
                                
                            else:
                                
                                LineItems1["InvoiceDiscountedAmountExTax"] = round(
                                    sage_bill1[i]["Lines"][k]["Exclusive"], 2)

                            for l in range(0, len(sage_coa1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_coa1[l]["ID"]:
                                    for n in range(0, len(reckon_coa1)):
                                        if sage_coa1[l]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                            LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                            LineItems1["AccountingCategoryId"] = reckon_coa1[n].get(
                                                "Id", None)
                                            logging.info(f"account data --> {LineItems1['AccountId']} ")
                                            break
                                        else:
                                            LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"

                            tax_grp_id = {}
                            for i1 in range(0, len(sage_coa1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_coa1[i1]["ID"]:
                                    Accounttype_data = get_account_type(
                                        sage_coa1[i1]["Category"]["ID"]),
                                    single_element = Accounttype_data[0]
                                    QuerySet1["TYPE"] = single_element
                                    QuerySet1["AccountType"] = get_account_type_id(
                                        sage_coa1[i1]["Category"]["ID"])
                                
                                    for t in range(0,len(sage_tax)):
                                        for m in range(0, len(taxcode_reckon)):
                                            if sage_bill1[i]['Tax'] == 0:
                                                if sage_tax[t]["Name"] == "No Tax":
                                                    if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            continue
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            continue

                                            if "TaxTypeId" in sage_bill1[i]['Lines'][k]:

                                                if sage_bill1[i]['Lines'][k]["TaxTypeId"] == 0:
                                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        break
                                            

                                                elif sage_bill1[i]['Lines'][k]["TaxTypeId"] == sage_tax[t]["ID"]:
                                                    if sage_tax[t]["Name"] in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales","Sales GST","GST sales (GST)","GST","Sales - With GST"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                    elif sage_tax[t]["Name"] == "Manual Tax":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
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

                                                    elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "GST 0%":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'INP':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCI':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'CAG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-Capital Purchase inc GST"]: 
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                            #     else:
                                            #         if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            #             tax_grp_id = taxcode_reckon[m]['ID']
                                            #             continue
                                            else:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    continue
                            
                                            LineItems1["TaxGroupId"] = tax_grp_id

                            QuerySet1["LineItems"].append(LineItems1)

                    payload = json.dumps(QuerySet1)
                    print(payload,"print payload ============")

                    url = f"{base_url}/bills"
                    asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_bill,
                            _id, job_id, task_id, sage_bill1[i]["ID"]))
                elif sage_bill1[i].get("Total") < 0:
                    _id = sage_bill1[i]["_id"]
                    QuerySet1 = {"LineItems": []}

                    QuerySet1["SupplierCreditNoteDate"] = sage_bill1[i].get(
                        "Date", None)
                    QuerySet1["Amount"] = abs(round(sage_bill1[i].get("Total"),2))
                    QuerySet1["Tax"] = abs(sage_bill1[i].get("Tax"))
                    if "DocumentNumber" in sage_bill1[i]:
                        QuerySet1["Reference"]=sage_bill1[i].get("DocumentNumber")+"-"+sage_bill1[i].get("Reference",None)
                        QuerySet1["SupplierCreditNoteNumber"] = sage_bill1[i].get("DocumentNumber")
                    
                    else:
                        QuerySet1["Reference"]=sage_bill1[i].get("ID")+"-"+sage_bill1[i].get("Reference",None)
                        QuerySet1["SupplierCreditNoteNumber"] = sage_bill1[i].get("ID")
                    
                    QuerySet1["TemplateId"] = templateid

                    if sage_bill1[i].get("Inclusive") == True:

                        QuerySet1["AmountTaxStatus"] = 2
                    else:
                        QuerySet1["AmountTaxStatus"] = 3

                    for k in range(0, len(reckon_supplier1)):
                        if sage_bill1[i]["SupplierName"].lower().strip() == reckon_supplier1[k]["FirstNameBranchName"].lower().strip():
                            QuerySet1["SupplierId"] = reckon_supplier1[k]["ContactId"]
                            break
                        else:
                            QuerySet1["SupplierId"] = "00000000-0000-0000-0000-000000000000"

                    total_lines = 0
                    for k in range(0, len(sage_bill1[i]['Lines'])):
                        
                        LineItems1 = {}
                        total_lines += len(sage_bill1[i]['Lines'])
                        if sage_bill1[i]['Lines'][k]["LineType"] == 0:
                            LineItems1["LineNo"] = total_lines
                            LineItems1["Item"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            LineItems1['TaxIsModified']=True
                            for p in range(0, len(sage_item1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_item1[p]["ID"]:
                                    logging.info(f"{job_id} match id ")
                                    for q in range(0, len(reckon_item1)):
                                        if sage_item1[p]["Code"] == reckon_item1[q]["FullName"]:
                                            LineItems1['ChargeableItemId'] = reckon_item1[q]["Id"]
                                            LineItems1["AccountingCategoryId"] = reckon_item1[q].get(
                                                "PurchaseCategoryId", None)
                                            break
                                        else:
                                            LineItems1['ChargeableItemId'] = "00000000-0000-0000-0000-000000000000"

                            LineItems1["TaxAmount"] = abs(sage_bill1[i]['Lines'][k]['Tax'])
                            LineItems1["InvoiceDiscountedTaxAmount"] = abs(round(sage_bill1[i]['Lines'][k]['Tax'],2))

                            LineItems1["InvoiceDiscountedAmountExTax"] = abs(round(sage_bill1[i]["Lines"][k]["Exclusive"],2))
                            # if QuerySet1["AmountTaxStatus"] == 3:
                            #     LineItems1["InvoiceDiscountedAmountExTax"] = round(
                            #         sage_bill1[i]["Lines"][k]["Exclusive"], 2)
                            #     LineItems1["UnitPriceExTax"] = round(
                            #         sage_bill1[i]["Lines"][k].get("UnitPriceExclusive", 0.0), 2)
                            # else:
                            #     LineItems1["UnitPriceExTax"] = round(
                            #         sage_bill1[i]["Lines"][k].get("UnitPriceInclusive", 0.0), 2)
                            #     LineItems1["InvoiceDiscountedAmountExTax"] = round(
                            #         sage_bill1[i]["Lines"][k]["Exclusive"], 2)

                            # LineItems1["UnitPriceIsTaxInclusive"] = round(sage_bill1[i]["Lines"][k].get(
                            #     "UnitPriceInclusive") - sage_bill1[i]["Lines"][k].get("UnitPriceExclusive"), 2)

                            LineItems1["Amount"] = abs(round(sage_bill1[i]['Lines'][k]["Total"],2))
                            LineItems1["AmountExTax"] = abs(round(sage_bill1[i]["Lines"][k]["Exclusive"],2))

                            LineItems1["AccountId"] = None
                            LineItems1["Description"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            LineItems1["Quantity"] = sage_bill1[i]["Lines"][k].get(
                                "Quantity", 1)

                            tax_grp_id = {}
                            for t in range(0,len(sage_tax)):
                                for m in range(0, len(taxcode_reckon)):
                                    if "TaxTypeId" in sage_bill1[i]['Lines']:
                                        if sage_bill1[i]['Lines']['TaxTypeId'] == sage_tax[t]["ID"] :
                                            # if sage_tax[t]["Name"] == "No Tax":
                                            #     if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            #         tax_grp_id = taxcode_reckon[m]['ID']
                                            #         break

                                            if sage_tax[t]["Name"] in  ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]:
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
                                            
                                    LineItems1["TaxGroupId"] = tax_grp_id

                            QuerySet1["LineItems"].append(LineItems1)

                        elif sage_bill1[i]['Lines'][k]["LineType"] == 1:
                            LineItems1["LineNo"] = total_lines
                            LineItems1["Description"] = sage_bill1[i]['Lines'][k].get(
                                "Description", None)
                            LineItems1["Quantity"] = sage_bill1[i]["Lines"][k].get(
                                "Quantity", 1)
                            LineItems1["TaxAmount"] = abs(sage_bill1[i]['Lines'][k].get(
                                'Tax', 0.0))
                            LineItems1["Amount"] = abs(round(sage_bill1[i]['Lines'][k]["Total"],2))
                            LineItems1["AmountExTax"] =abs(round(sage_bill1[i]["Lines"][k]["Exclusive"],2))
                            LineItems1['ChargeableItemId'] = None
                            LineItems1['TaxIsModified']=True
                            LineItems1["InvoiceDiscountedTaxAmount"] = abs(round(sage_bill1[i]['Lines'][k]['Tax'],2))

                            LineItems1["InvoiceDiscountedAmountExTax"] = abs(round(sage_bill1[i]["Lines"][k]["Exclusive"],2))
                        

                            # if QuerySet1["AmountTaxStatus"] == 3:
                            #     LineItems1["InvoiceDiscountedAmountExTax"] = round(
                            #         sage_bill1[i]["Lines"][k]["Exclusive"], 2)
                            #     LineItems1["UnitPriceExTax"] = round(
                            #         sage_bill1[i]["Lines"][k].get("UnitPriceExclusive", 0.0), 2)
                            # else:
                            #     LineItems1["UnitPriceExTax"] = round(
                            #         sage_bill1[i]["Lines"][k].get("UnitPriceInclusive", 0.0), 2)
                            #     LineItems1["InvoiceDiscountedAmountExTax"] = round(
                            #         sage_bill1[i]["Lines"][k]["Exclusive"], 2)

                            for l in range(0, len(sage_coa1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_coa1[l]["ID"]:
                                    for n in range(0, len(reckon_coa1)):
                                        if sage_coa1[l]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                            LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                            LineItems1["AccountingCategoryId"] = reckon_coa1[n].get(
                                                "Id", None)
                                            logging.info(f"{job_id} account data-->{LineItems1['AccountId']} ")
                                            break
                                        else:
                                            LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"

                            tax_grp_id = {}
                            for i1 in range(0, len(sage_coa1)):
                                if sage_bill1[i]['Lines'][k]["SelectionId"] == sage_coa1[i1]["ID"]:
                                    Accounttype_data = get_account_type(
                                        sage_coa1[i1]["Category"]["ID"]),
                                    single_element = Accounttype_data[0]
                                    QuerySet1["TYPE"] = single_element
                                    QuerySet1["AccountType"] = get_account_type_id(
                                        sage_coa1[i1]["Category"]["ID"])
                                
                                    for t in range(0,len(sage_tax)):
                                        for m in range(0, len(taxcode_reckon)):
                                            if sage_bill1[i]['Tax'] == 0:
                                                if sage_tax[t]["Name"] == "No Tax":
                                                    if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            continue
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            continue

                                            if "TaxTypeId" in sage_bill1[i]['Lines'][k]:
                                                if sage_bill1[i]['Lines'][k]["TaxTypeId"] == sage_tax[t]["ID"]:
                                                    if sage_tax[t]["Name"] in  ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                    elif sage_tax[t]["Name"] == "Manual Tax":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                    # elif sage_tax[t]["Name"] == "No Tax":
                                                    #     if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                    #         if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    #             tax_grp_id = taxcode_reckon[m]['ID']
                                                    #             break
                                                    #     else:
                                                    #         if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    #             tax_grp_id = taxcode_reckon[m]['ID']
                                                    #             break

                                                    elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "GST 0%":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'INP':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCI':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'CAG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'FRE':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCF':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] in ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-Capital Purchase inc GST"]:
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break

                                                    elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                                            if taxcode_reckon[m]["Name"] == 'GST':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                                        else:
                                                            if taxcode_reckon[m]["Name"] == 'NCG':
                                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                                break
                                            #     else:
                                            #         if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            #             tax_grp_id = taxcode_reckon[m]['ID']
                                            #             continue
                                            else:
                                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                    tax_grp_id = taxcode_reckon[m]['ID']
                                                    continue
                            
                                            LineItems1["TaxGroupId"] = tax_grp_id

                            QuerySet1["LineItems"].append(LineItems1)

                    payload = json.dumps(QuerySet1)

                    url_vendorcredite = f"{base_url}/suppliercreditnotes"
                    asyncio.run(post_data_in_reckon(url_vendorcredite, post_headers, payload, sage_bill,
                                _id, job_id, task_id, sage_bill1[i]["ID"]))
                    

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)