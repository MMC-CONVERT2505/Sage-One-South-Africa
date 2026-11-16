import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_reckon_chart_of_account(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_chart_of_account")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url1 = f"{base_url}/accounts"
        url2 = f"{base_url}/bankaccounts"

        sage_coa = dbname['sage_coa']

        x = sage_coa.find({"job_id": job_id,"is_pushed":0})
        sage_coa1 = []
        for k in x:
            sage_coa1.append(k)

        reckon_coa1 = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa = []
        for p1 in reckon_coa1:
            reckon_coa.append(p1)

        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)


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

        for i in range(0, len(sage_coa1)):
            if sage_coa1[i]["AccountType"] != 3:

                _id = sage_coa1[i]["_id"]

                QuerySet1 = {}
                QuerySet1["AccountName"] = sage_coa1[i]["Name"].replace(":", " ")
                Accounttype_data = get_account_type(
                    sage_coa1[i]["Category"]["ID"]),
                single_element = Accounttype_data[0]
                QuerySet1["TYPE"] = single_element
                QuerySet1["AccountType"] = get_account_type_id(
                    sage_coa1[i]["Category"]["ID"])
                QuerySet1["AccountCode"] = sage_coa1[i]["ID"]
                for j in range(0, len(reckon_coa)):
                    if sage_coa1[i]["Name"] == reckon_coa[j]["Name"]:
                        QuerySet1["ParentAccountingCategoryId"] = reckon_coa[j]["Id"]
                    else:
                        QuerySet1["ParentAccountingCategoryId"] = "00000000-0000-0000-0000-000000000000"

                QuerySet1["Status"] = 1
                QuerySet1["BankAccountStatus"] = 1

                EFT = {}
                EFT['AccountName'] = sage_coa1[i]["Name"].replace(":", " ")
                EFT['EFT1'] = sage_coa1[i]["ID"]
                BulkElectronicPaymentSettings = {}
                BulkElectronicPaymentSettings['AccountName'] = sage_coa1[i]["Name"].replace(":", " ")
                QuerySet1["BulkElectronicPaymentSettings"] = BulkElectronicPaymentSettings
                QuerySet1["EFT"] = EFT

                QuerySet1["Description"] = sage_coa1[i]["Description"]
                tax_grp_id={}

                for t in range(0,len(sage_tax)):
                    for m in range(0, len(taxcode_reckon)):
                    
                        if "DefaultTaxTypeId" in sage_coa1[i]:
                            if sage_coa1[i]["DefaultTaxTypeId"] == 0:
                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    tax_grp_id = taxcode_reckon[m]['ID']
                                    break

                            elif sage_coa1[i]["DefaultTaxTypeId"] == sage_tax[t]["ID"]:
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

                                elif sage_tax[t]["Name"] in ["Export Sales - GST Free","GST Free"]:
                                    if QuerySet1["TYPE"] in ["Sales","Other Income","Other GST-Free Sales"]:
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

                                elif sage_tax[t]["Name"] in ["Purchases - GST Free","GST Free Purchases"]:
                                    if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                        if taxcode_reckon[m]["Name"] == 'FRE':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break
                                    else:
                                        if taxcode_reckon[m]["Name"] == 'NCF':
                                            tax_grp_id = taxcode_reckon[m]['ID']
                                            break

                                elif sage_tax[t]["Name"] in ["Non-Capital Purchases","Non-capital purchases (INP)"]:
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

                                elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
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

                            # 
                            else:
                                if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    tax_grp_id = taxcode_reckon[m]['ID']
                                    break

                        else:
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                tax_grp_id = taxcode_reckon[m]['ID']
                                break
                        if tax_grp_id != None:
                            QuerySet1["TaxGroupId"] = tax_grp_id

                payload = json.dumps(QuerySet1)

                asyncio.run(post_data_in_reckon(url1, post_headers, payload,
                            sage_coa, _id, job_id, task_id, sage_coa1[i]["Name"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

