import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
from apps.home.data_util import get_job_details
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config


def add_invoice_credit_note(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside invoice credit notes data ")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/creditnotes"

        sage_creditnote = dbname['sage_credit_note']

        x = sage_creditnote.find({"job_id": job_id,"is_pushed":0})
        sage_creditnote1 = []
        for k in x:
            sage_creditnote1.append(k)

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

        reckon_item = dbname["reckon_item"].find({"job_id": job_id})
        reckon_item1 = []
        for p01 in reckon_item:
            reckon_item1.append(p01)

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

        for i in range(0, len(sage_creditnote1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_creditnote1[i]["Date"] and end_date >= sage_creditnote1[i]["Date"] :
                print(sage_creditnote1[i],"sage_creditnote1============")

                _id = sage_creditnote1[i]["_id"]
                QuerySet1 = {"LineItems": []}
                QuerySet1["DueDate"] = sage_creditnote1[i].get("DueDate", None)
                QuerySet1["CreditNoteDate"] = sage_creditnote1[i].get("Date", None)
                QuerySet1["Notes"] = sage_creditnote1[i].get("Message", None)
                QuerySet1["PaymentDetails"] = sage_creditnote1[i].get("", None)
                QuerySet1["Amount"] = sage_creditnote1[i].get("Total")
                QuerySet1["Tax"] = sage_creditnote1[i].get("Tax")

                if "DocumentNumber" in sage_creditnote1[i]:
                    QuerySet1["Reference"] = sage_creditnote1[i].get(
                        "DocumentNumber")+"-"+sage_creditnote1[i].get("Reference", None)
                    QuerySet1["CreditNoteNumber"] = sage_creditnote1[i].get(
                        "DocumentNumber")+"-"+sage_creditnote1[i].get("Reference", None)
                else:
                    QuerySet1["Reference"] = sage_creditnote1[i].get(
                        "ID")+"-"+sage_creditnote1[i].get("Reference", None)
                    QuerySet1["InvoiceNumber"] = sage_creditnote1[i].get("ID")

                if sage_creditnote1[i].get("Inclusive") == True:

                    QuerySet1["AmountTaxStatus"] = 2
                else:
                    QuerySet1["AmountTaxStatus"] = 3

                for k in range(0, len(reckon_customer1)):
                    if sage_creditnote1[i]["CustomerName"].lower().strip() == reckon_customer1[k]["FirstNameBranchName"].lower().strip():
                        QuerySet1["CustomerId"] = reckon_customer1[k]["ContactId"]
                        break
                    else:
                        QuerySet1["CustomerId"] = "00000000-0000-0000-0000-000000000000"

                total_lines = 0
                for k in range(0, len(sage_creditnote1[i]['Lines'])):
                    LineItems1 = {}
                    total_lines += len(sage_creditnote1[i]['Lines'])
                    if sage_creditnote1[i]['Lines'][k]["LineType"] == 0:
                        LineItems1['TaxIsModified'] = True
                        LineItems1["Item"] = sage_creditnote1[i]['Lines'][k].get(
                            "Description", None)

                        LineItems1["LineNo"] = total_lines
                        for p in range(0, len(sage_item1)):
                            if sage_creditnote1[i]['Lines'][k]["SelectionId"] == sage_item1[p]["ID"]:
                                logging.info(f"{job_id}  match id ")
                                for q in range(0, len(reckon_item1)):
                                    if sage_item1[p]["Code"] == reckon_item1[q]["FullName"]:
                                        LineItems1['ChargeableItemId'] = reckon_item1[q]["Id"]
                                        break
                                    else:
                                        LineItems1['ChargeableItemId'] = "00000000-0000-0000-0000-000000000000"

                        LineItems1["TaxAmount"] = sage_creditnote1[i]['Lines'][k]['Tax']

                        # if QuerySet1["AmountTaxStatus"] == 3:

                        #     LineItems1["UnitPriceExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceInclusive",0.0)
                        # else:

                        #     LineItems1["UnitPriceExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceExclusive",0.0)

                        LineItems1["Amount"] = sage_creditnote1[i]['Lines'][k]["Total"]
                        LineItems1["AmountExTax"] = sage_creditnote1[i]["Lines"][k]["Exclusive"]

                        LineItems1["AccountId"] = None
                        LineItems1["Description"] = sage_creditnote1[i]['Lines'][k].get(
                            "Comments", None)
                        LineItems1["Quantity"] = sage_creditnote1[i]["Lines"][k].get(
                            "Quantity", 1)

                        # if QuerySet1["AmountTaxStatus"] == 3:

                        #     LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceInclusive",0.0)
                        # else:

                        #     LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceExclusive",0.0)

                        LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("Exclusive",0.0)
                    
                        LineItems1["InvoiceDiscountedTaxAmount"]= sage_creditnote1[i]['Lines'][k]['Tax']

                        tax_grp_id = {}

                        for t in range(0, len(sage_tax)):
                            for m in range(0, len(taxcode_reckon)):
                                if sage_creditnote1[i]['Tax'] == 0:
                                    if sage_tax[t]["Name"] == "No Tax":
                                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break

                                if "TaxTypeId" in sage_creditnote1[i]['Lines'][k]:
                                    if sage_creditnote1[i]['Lines'][k]["TaxTypeId"] == sage_tax[t]["ID"]:
                                        if sage_tax[t]["Name"]  in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]: 
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

                    elif sage_creditnote1[i]['Lines'][k]["LineType"] == 1:

                        LineItems1["Description"] = sage_creditnote1[i]['Lines'][k].get(
                            "Description", None)
                        
                        LineItems1["LineNo"] = total_lines
                        LineItems1["Quantity"] = sage_creditnote1[i]["Lines"][k].get(
                            "Quantity", 1)
                        LineItems1["TaxAmount"] = sage_creditnote1[i]['Lines'][k].get(
                            'Tax', 0.0)
                        # LineItems1["LineNo"]=total_lines
                        # LineItems1["UnitPriceTax"]= sage_creditnote1[i]["Lines"][k].get("UnitPriceInclusive")-sage_creditnote1[i]["Lines"][k].get("UnitPriceExclusive")

                        # if QuerySet1["AmountTaxStatus"] == 3:
                        #     LineItems1["UnitPriceExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceInclusive",0.0)
                        # else:
                        #       LineItems1["UnitPriceExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceExclusive",0.0)

                        LineItems1["Amount"] = sage_creditnote1[i]['Lines'][k]["Total"]
                        LineItems1["AmountExTax"] = sage_creditnote1[i]["Lines"][k]["Exclusive"]
                        LineItems1['ChargeableItemId'] = None
                        LineItems1['TaxIsModified'] = True

                        # if QuerySet1["AmountTaxStatus"] == 3:
                        #     LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceInclusive",0.0)
                        # else:
                        #     LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("UnitPriceExclusive",0.0)

                        LineItems1["InvoiceDiscountedAmountExTax"]=sage_creditnote1[i]["Lines"][k].get("Exclusive",0.0)
                        LineItems1["InvoiceDiscountedTaxAmount"]= sage_creditnote1[i]['Lines'][k]['Tax']

                        for l in range(0, len(sage_coa1)):
                            if sage_creditnote1[i]['Lines'][k]["SelectionId"] == sage_coa1[l]["ID"]:
                                for n in range(0, len(reckon_coa1)):
                                    if sage_coa1[l]["Name"] == reckon_coa1[n]["Name"]:
                                        LineItems1['AccountId'] = reckon_coa1[n]["Id"]
                                        break
                                    else:
                                        LineItems1['AccountId'] = "00000000-0000-0000-0000-000000000000"

                        tax_grp_id = {}
                        for i1 in range(0, len(sage_coa1)):
                            if sage_creditnote1[i]['Lines'][k]["SelectionId"] == sage_coa1[i1]["ID"]:
                                Accounttype_data = get_account_type(
                                    sage_coa1[i1]["Category"]["ID"]),
                                single_element = Accounttype_data[0]
                                QuerySet1["TYPE"] = single_element
                                QuerySet1["AccountType"] = get_account_type_id(
                                    sage_coa1[i1]["Category"]["ID"])

                                for t in range(0, len(sage_tax)):
                                    for m in range(0, len(taxcode_reckon)):
                                        if sage_creditnote1[i]['Tax'] == 0:
                                            if sage_tax[t]["Name"] == "No Tax":
                                                if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        continue
                                                else:
                                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                        tax_grp_id = taxcode_reckon[m]['ID']
                                                        continue

                                        if "TaxTypeId" in sage_creditnote1[i]['Lines'][k]:
                                            if sage_creditnote1[i]['Lines'][k]["TaxTypeId"] == sage_tax[t]["ID"]:
                                                if sage_tax[t]["Name"]  in ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]: 
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                elif sage_tax[t]["Name"] == "Manual Tax":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
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
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == "GST 0%":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCF':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCF':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'INP':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCI':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'CAG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCF':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCF':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break

                                                elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                                    if QuerySet1["TYPE"] in ["Sales", "Other Income"]:
                                                        if taxcode_reckon[m]["Name"] == 'GST':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                                    else:
                                                        if taxcode_reckon[m]["Name"] == 'NCG':
                                                            tax_grp_id = taxcode_reckon[m]['ID']
                                                            break
                                        else:
                                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                tax_grp_id = taxcode_reckon[m]['ID']

                                        LineItems1["TaxGroupId"] = tax_grp_id
                        QuerySet1["LineItems"].append(LineItems1)

                payload = json.dumps(QuerySet1)
                print(payload, "payload data ====")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_creditnote,
                            _id, job_id, task_id, sage_creditnote1[i]["ID"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
