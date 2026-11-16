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

def add_trial_balance_journal_reckon(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_trial_balance_journal_reckon")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/journals"

        sage_trial_balance_journal = dbname['sage_trial_balance']

        x = sage_trial_balance_journal.find({"job_id": job_id,"is_pushed":0})
        sage_trial_balance_journal1 = []
        for k in x:
            sage_trial_balance_journal1.append(k)

        sage_bank = dbname['sage_bank']
        x01 = sage_bank.find({"job_id": job_id})
        sage_bank1 = []
        for k02 in x01:
            sage_bank1.append(k02)

        reckon_bank_accounts= dbname["reckon_bank_account"].find({"job_id": job_id})
        reckon_bank1 = []
        for k11 in reckon_bank_accounts:
            reckon_bank1.append(k11)


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
        

        QuerySet1 = {"Transactions": []}
        
        for i in range(0, len(sage_trial_balance_journal1)):
            _id = sage_trial_balance_journal1[i]["_id"]
            QuerySet1["JournalDate"]=sage_trial_balance_journal1[i].get("Date",None)
            QuerySet1["JournalStatus"]=2
            QuerySet1["Summary"]="Conversion_trial_balance"
            QuerySet1["JournalNumber"]="Conversion_trial_balance"
            QuerySet1["AmountTaxStatus"]=3

            transactionlinedebit = {}


            total_debit = 0
            total_credit = 0

            if "Debit" in sage_trial_balance_journal1[i]:
                total_debit += sage_trial_balance_journal1[i]["Debit"]
            if "Credit" in sage_trial_balance_journal1[i]:
                total_credit += sage_trial_balance_journal1[i]["Credit"]

            rounding_amount=total_credit-total_debit


            transactionlinedebit = {}


            # if sage_trial_balance_journal1[i]["Name"] == "System Rounding":
            #     if rounding_amount > 0:
            #         transactionlinedebit["Debit"]=abs(round(rounding_amount,2))
            #         transactionlinedebit["TaxAmount"]=0

            #         tax_grp_id = {}

            #         for m in range(0, len(taxcode_reckon)):
            #             if taxcode_reckon[m]["Name"] == 'NO TAX':
            #                 tax_grp_id = taxcode_reckon[m]['ID']
            #                 transactionlinedebit["TransType"] = 1
            #                 break

            #         transactionlinedebit["TaxGroupId"] = tax_grp_id

            #         transactionlinedebit["TaxModified"] = True
            #         for n in range(0, len(reckon_coa1)):
            #             if reckon_coa1[n]["Name"] == "System Rounding":
            #                 transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
            #                 break
            #     elif rounding_amount < 0:
            #         transactionlinedebit["Credit"]=abs(round(rounding_amount,2))
            #         transactionlinedebit["TaxAmount"]=0

            #         tax_grp_id = {}

            #         for m in range(0, len(taxcode_reckon)):
            #             if taxcode_reckon[m]["Name"] == 'NO TAX':
            #                 tax_grp_id = taxcode_reckon[m]['ID']
            #                 transactionlinedebit["TransType"] = 1
            #                 break

            #         transactionlinedebit["TaxGroupId"] = tax_grp_id

            #         transactionlinedebit["TaxModified"] = True
            #         for n in range(0, len(reckon_coa1)):
            #             if reckon_coa1[n]["Name"] == "System Rounding":
            #                 transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
            #                 break

            if sage_trial_balance_journal1[i]["Debit"] != 0:
                if sage_trial_balance_journal1[i]["Name"] != "System Rounding":
                    transactionlinedebit["Debit"]=round(abs(sage_trial_balance_journal1[i].get("Debit",0.0)),2)
                    transactionlinedebit["TaxAmount"]=0

                    tax_grp_id = {}

                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            transactionlinedebit["TransType"] = 1
                            break

                    transactionlinedebit["TaxGroupId"] = tax_grp_id

                    transactionlinedebit["TaxModified"] = True

                    for p in range(0, len(sage_coa1)):
                        for n in range(0, len(reckon_coa1)):
                            if sage_trial_balance_journal1[i].get("AccountId") == sage_coa1[p]["ID"]:
                                if sage_coa1[p]["Name"] == reckon_coa1[n]["Name"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break
                                elif sage_coa1[p]["Name"].lower().replace(":", " ") == reckon_coa1[n]["Name"].lower().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            elif sage_trial_balance_journal1[i]["Name"].lower().strip().replace(":", " ") == sage_coa1[p]["Name"].lower().strip().replace(":", " "):
                                if sage_coa1[p]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            
                            elif sage_trial_balance_journal1[i]["Name"] in ["Tax Provision","Tax Payable"]:
                                if reckon_coa1[n]["Name"] in  ["GST Collected"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            elif sage_trial_balance_journal1[i]["Name"] in  ["retained income (opening balance)", "trade receivables",
                                                    "trade payables", "retained income","Trade Receivables","Retained Income"]:
                                if reckon_coa1[n]["Name"] in  ["Retained Earnings Surplus/(Accumulated Losses)"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            
                            elif sage_trial_balance_journal1[i]["Name"] in  "Opening Balance and Tax Adjustments":
                                if reckon_coa1[n]["Name"] in  ["Opening Balance Equity"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            else:
                                if sage_trial_balance_journal1[i]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n][
                                    "Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

            
            elif sage_trial_balance_journal1[i]["Credit"] != 0:
                if sage_trial_balance_journal1[i]["Name"] != "System Rounding":
                    transactionlinedebit["Credit"]=round(abs(sage_trial_balance_journal1[i].get("Credit",0.0)),2)
                    transactionlinedebit["TaxAmount"]=0
                    tax_grp_id = {}
                    for m in range(0, len(taxcode_reckon)):
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            tax_grp_id = taxcode_reckon[m]['ID']
                            transactionlinedebit["TransType"] = 1
                            break

                    transactionlinedebit["TaxGroupId"] = tax_grp_id

                    transactionlinedebit["TaxModified"] = True
                    for p in range(0, len(sage_coa1)):
                        for n in range(0, len(reckon_coa1)):
                            
                            if sage_trial_balance_journal1[i].get("AccountId") == sage_coa1[p]["ID"]:
                                
                                if sage_coa1[p]["Name"].lower().strip() == reckon_coa1[n]["Name"].lower().strip():
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break
                                elif sage_coa1[p]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            elif sage_trial_balance_journal1[i]["Name"].lower().strip() == sage_coa1[p]["Name"].lower().strip():
                                if sage_coa1[p]["Name"].lower().strip() == reckon_coa1[n]["Name"].lower().strip():
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            elif sage_trial_balance_journal1[i]["Name"] in  ["Tax Provision","Tax Payable"]:
                                if reckon_coa1[n]["Name"] in  ["GST Collected"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            elif sage_trial_balance_journal1[i]["Name"] in  ["retained income (opening balance)", "trade receivables",
                                                "trade payables", "retained income","Trade Receivables","Retained Income"]:
                                if reckon_coa1[n]["Name"] in  ["Retained Earnings Surplus/(Accumulated Losses)"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                        
                            elif sage_trial_balance_journal1[i]["Name"] in  "Opening Balance and Tax Adjustments":
                                if reckon_coa1[n]["Name"] in ["Opening Balance Equity"]:
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break

                            else:
                                if sage_trial_balance_journal1[i]["Name"].lower().strip().replace(":", " ") == reckon_coa1[n][
                                    "Name"].lower().strip().replace(":", " "):
                                    transactionlinedebit["AccountingCategoryId"] = reckon_coa1[n]["Id"]
                                    break
                                
            if transactionlinedebit != None and transactionlinedebit != {}:
                QuerySet1["Transactions"].append(transactionlinedebit)


        payload = json.dumps(QuerySet1)  
        print(payload,"payload =====")

        asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_trial_balance_journal,
                    _id, job_id, task_id, sage_trial_balance_journal1[i]["Name"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)