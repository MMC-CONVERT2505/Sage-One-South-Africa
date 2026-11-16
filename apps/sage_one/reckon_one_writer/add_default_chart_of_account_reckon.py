import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config


def add_reckon_default_chart_of_account(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_default_chart_of_account")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url1 = f"{base_url}/accounts"
        _id="66092041848869eed5fef664"

        sage_coa = dbname['sage_coa']
        x = sage_coa.find({"job_id": job_id,"is_pushed":0})
        sage_coa1 = []
        for k in x:
            sage_coa1.append(k)

        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        print(taxcode_reckon,"taxcode_reckon=======")

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

        sage_default_coa=[{"Name":"Sales",
                           "Category_Id":1,
                           "ID":"9991",
                           "Description":"SalesAccount",
                           "DefaultTaxTypeId":11
                           },
                          
                          {"Name":"Purchases",
                           "Category_Id":2,
                           "ID":"9992",
                           "Description":"PurchasesAccount",
                           },
                           
                          {"Name":"Item Adjustments",
                           "Category_Id":2,
                           "ID":"9993",
                           "Description":"ItemAdjustmentsAccount",
                           },
                           {"Name":"Discount Received",
                           "Category_Id":1,
                           "ID":"9994",
                           "Description":"DiscountReceivedAccount",
                           },

                           {"Name":"Customer Document Rounding",
                           "Category_Id":10,
                           "ID":"9995",
                           "Description":"DiscountReceivedAccount",
                           },

                           {"Name":"Bad Debts",
                           "Category_Id":10,
                           "ID":"9996",
                           "Description":"DiscountReceivedAccount",
                           },

                           {"Name":"Discount Allowed",
                           "Category_Id":10,
                           "ID":"9997",
                           "Description":"DiscountReceivedAccount",
                           },
                           {"Name":"Inventory",
                           "Category_Id":6,
                           "ID":"9998",
                           "Description":"DiscountReceivedAccount",
                           },
                           {"Name":"System Rounding",
                           "Category_Id":9,
                           "ID":"9999",
                           "Description":"SystemRounding"
                           },
                           ]

        for i in range(0, len(sage_default_coa)):
            QuerySet1 = {}
            QuerySet1["AccountName"] = sage_default_coa[i]["Name"]
            Accounttype_data = get_account_type(
                sage_default_coa[i]["Category_Id"]),
            single_element = Accounttype_data[0]
            QuerySet1["TYPE"] = single_element
            QuerySet1["AccountType"] = get_account_type_id(
                sage_default_coa[i]["Category_Id"])
            QuerySet1["AccountCode"] = sage_default_coa[i]["ID"]
            # for j in range(0, len(reckon_coa)):
            #     if sage_coa1[i]["Name"] == reckon_coa[j]["Name"]:
            #         QuerySet1["ParentAccountingCategoryId"] = reckon_coa[j]["Id"]
            #     else:
            QuerySet1["ParentAccountingCategoryId"] = "00000000-0000-0000-0000-000000000000"

            QuerySet1["Status"] = 1
            QuerySet1["BankAccountStatus"] = 1

            EFT = {}
            EFT['AccountName'] = sage_default_coa[i]["Name"]
            EFT['EFT1'] = sage_default_coa[i]["ID"]
            BulkElectronicPaymentSettings = {}
            BulkElectronicPaymentSettings['AccountName'] = sage_default_coa[i]["Name"]
            QuerySet1["BulkElectronicPaymentSettings"] = BulkElectronicPaymentSettings
            QuerySet1["EFT"] = EFT

            QuerySet1["Description"] = sage_default_coa[i]["Description"]
            tax_grp_id={}

            for m in range(0, len(taxcode_reckon)):
                if taxcode_reckon[m]["Name"] == 'FRE':
                    tax_grp_id = taxcode_reckon[m]['ID']
                    break
                
            QuerySet1["TaxGroupId"] = tax_grp_id

            payload = json.dumps(QuerySet1)

            print(payload,"payload print data======")

            asyncio.run(post_data_in_reckon(url1, post_headers, payload,
                        sage_coa, _id, job_id, task_id, sage_default_coa[i]["Name"]))

    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)

