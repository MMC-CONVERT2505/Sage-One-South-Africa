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

def add_spend_money(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_spend_money")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/payments"
    
        sage_spend = dbname['sage_spend_money']

        x = sage_spend.find({"job_id": job_id,"is_pushed":0})
        sage_spend1 = []
        for k in x:
            sage_spend1.append(k)

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

        taxcode_sage1 = dbname["sage_tax"].find({"job_id": job_id})
        taxcode_sage = []
        for p1 in taxcode_sage1:
            taxcode_sage.append(p1)

        
        reckon_item = dbname["reckon_item"].find({"job_id": job_id})
        reckon_item1 = []
        for p01 in reckon_item:
            reckon_item1.append(p01)

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

        for i in range(0, len(sage_spend1)):
            start_date,end_date=get_job_details(job_id)

            if start_date <= sage_spend1[i]["Date"] and end_date >= sage_spend1[i]["Date"]:
                _id = sage_spend1[i]["_id"]
                QuerySet1 = {"AllocationSplit": []}
                BankAccountId={}
                ContactId={}
                AccountsPayableCategoryId=None
                QuerySet1["TransDate"]=sage_spend1[i]["Date"]
                QuerySet1["Amount"]=sage_spend1[i]["Total"]
                QuerySet1["Details"]=sage_spend1[i]["Description"]
                if "Reference" in sage_spend1[i]:
                    QuerySet1["Reference"]=sage_spend1[i]["Reference"]
                else:
                    QuerySet1["Reference"]=sage_spend1[i]["ID"]


                for a in range(0,len(sage_bank1)):
        
                    if sage_spend1[i]["BankAccountId"] == sage_bank1[a]["ID"]:
                        for b in range(0,len(reckon_bank1)):

                            if sage_bank1[a]["Name"].lower().strip() == reckon_bank1[b]["Description"].lower().strip():
                                BankAccountId=reckon_bank1[b]["BankAccountID"]
                                break
                            else:
                                BankAccountId="00000000-0000-0000-0000-000000000000"

                for k in range(0,len(reckon_supplier1)):
                    if 'Payee' in sage_spend1[i] and sage_spend1[i]["Payee"] not in[None,""] :
                        if sage_spend1[i]["Payee"].lower() == reckon_supplier1[k]["Description"].lower():
                            print(reckon_supplier1[k]["Description"],"reckon_supplier---------------")
                            ContactId=reckon_supplier1[k]["ContactId"]
                            break
                        elif sage_spend1[i]["Payee"] == "":
                            if reckon_supplier1[k]["Description"] == 'No Name - S':
                                ContactId=reckon_supplier1[k]["ContactId"]
                                continue
                    else:
                        if reckon_supplier1[k]["Description"] == 'No Name - S':
                            ContactId=reckon_supplier1[k]["ContactId"]
                            continue
                
                AllocationSplit1={}
                AllocationSplit1["LineNo"]=1
                if "Description" in sage_spend1[i]:
                    AllocationSplit1["Description"]=sage_spend1[i]["Description"]
                else:
                    AllocationSplit1["Description"]=None
                AllocationSplit1["Quantity"]=1
                AllocationSplit1["ProjectId"]="00000000-0000-0000-0000-000000000000"
                AllocationSplit1["UnitPricePrecision"]=2.0
                AllocationSplit1["TaxAmount"]=sage_spend1[i]["Tax"]
                AllocationSplit1["AmountExTax"]=sage_spend1[i]["Exclusive"]
                AllocationSplit1["DiscountAmountExTax"]=0
                AllocationSplit1["DiscountAmountTax"]=0
                AllocationSplit1["Amount"]=sage_spend1[i]["Total"]
                
                for l in range(0,len(sage_coa1)):
                    if sage_coa1[l]["ID"] ==sage_spend1[i].get("AccountId",0.0):
                        for n in range(0,len(reckon_coa1)):
                            if sage_coa1[l]["Name"].lower().strip().replace(":", " ")==reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                                AllocationSplit1['AccountId']=reckon_coa1[n]["Id"]
                                break
                            else:
                                AllocationSplit1['AccountId']="00000000-0000-0000-0000-000000000000"
                                continue

                tax_grp_id={}

                        
                for i1 in range(0, len(sage_coa1)):
                    
                    if sage_spend1[i]['AccountId'] == sage_coa1[i1]['ID']:
                        
                        QuerySet1["AccountName"] = sage_coa1[i1]["Name"]
                        Accounttype_data = get_account_type(
                            sage_coa1[i1]["Category"]["ID"]),
                        single_element = Accounttype_data[0]
                        QuerySet1["TYPE"] = single_element
                        QuerySet1["AccountType"] = get_account_type_id(
                            sage_coa1[i1]["Category"]["ID"])
                        QuerySet1["AccountCode"] = sage_coa1[i1]["ID"]
                    
                        for t in range(0,len(sage_tax)):
                            for m in range(0, len(taxcode_reckon)):
                                if sage_spend1[i]['Tax'] == 0:
                                    if sage_tax[t]["Name"] == "No Tax":
                                        if QuerySet1["TYPE"] in ["Sales","Other Income"]:
                                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                break
                                        else:
                                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                                tax_grp_id = taxcode_reckon[m]['ID']
                                                break


                                if "TaxTypeId" in sage_spend1[i]:
                                    if sage_spend1[i]["TaxTypeId"] == sage_tax[t]["ID"]:
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

                                        elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
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
                            
                                else:
                                    if taxcode_reckon[m]["Name"] == 'NO TAX':
                                        tax_grp_id = taxcode_reckon[m]['ID']
                                        break
                                    
                if tax_grp_id != None:
                    AllocationSplit1["TaxGroupId"] = tax_grp_id
                

                for n2 in range(0,len(reckon_coa1)):
                    if reckon_coa1[n2]['Name'] == 'Accounts Payable':
                        AccountsPayableCategoryId=reckon_coa1[n2]["Id"]
                        print(AccountsPayableCategoryId)
                        break

                QuerySet1['AccountsPayableCategoryId'] = AccountsPayableCategoryId
                QuerySet1["BankAccountId"]=BankAccountId
                QuerySet1["ContactId"]=ContactId
                QuerySet1["AllocationSplit"].append(AllocationSplit1)
                payload = json.dumps(QuerySet1)
                
                
                print(payload)
                print("-----------------------")

                asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_spend,
                        _id, job_id, task_id, sage_spend1[i]["Description"]))
                # else:
                #     _id = sage_spend1[i]["_id"]
                #     sage_spend.update_one({'_id': _id}, {"$set": {"payload":"Out of date"}}, upsert=True)
                
    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
