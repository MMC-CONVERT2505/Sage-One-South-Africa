import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config


def add_reckon_bank_account(job_id, task_id):
    logging = log_config(job_id)
    
    try:
        logging.info(f"{job_id} inside add_reckon_bank_account ")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url2 = f"{base_url}/bankaccounts"

        sage_bank = dbname['sage_bank']

        x = sage_bank.find({"job_id": job_id,"is_pushed":0})
        sage_bank1 = []
        for k in x:
            sage_bank1.append(k)
            
        for i in range(0, len(sage_bank1)):
            if sage_bank1[i]["PaymentMethod"] in [1,2,4]:
                _id = sage_bank1[i]["_id"]
                QuerySet1 = {}
                QuerySet1["AccountType"] =1
                QuerySet1["BankAccountStatus"] = 1
                EFT = {}
                EFT['AccountName'] = sage_bank1[i]["Name"]

                # account_str = str(sage_bank1[i]["ID"])

                # if len(account_str) ==5:
                #     EFT['EFT1']= '0' + account_str
                # elif len(account_str) ==4:
                #     EFT['EFT1']= '00' + account_str
                # elif len(account_str) ==3:
                #     EFT['EFT1']= '000' + account_str
                # elif len(account_str) ==2:
                #     EFT['EFT1']= '0000' + account_str
               
                
                if sage_bank1[i]["AccountNumber"] not in ["",None]:
                    EFT['EFT2'] = sage_bank1[i]["AccountNumber"]
                    if "BranchNumber" in sage_bank1[i] and sage_bank1[i]["BranchNumber"] != "":
                        split_branchnumber=sage_bank1[i]["BranchNumber"].replace("-","")
                        EFT['EFT1']=split_branchnumber

                    else:
                        EFT['EFT1']="000000"



                # else:
                #     if len(account_str) ==5:
                #         EFT['EFT2']= '0' + account_str
                #     elif len(account_str) ==4:
                #         EFT['EFT2']= '00' + account_str
                #     elif len(account_str) ==3:
                #         EFT['EFT2']= '000' + account_str
                #     elif len(account_str) ==2:
                #         EFT['EFT2']= '0000' + account_str
                        

                QuerySet1["EFT"] = EFT
                QuerySet1["Description"] = sage_bank1[i]["Name"]
                payload = json.dumps(QuerySet1)
                
                asyncio.run(post_data_in_reckon(url2, post_headers, payload,
                            sage_bank, _id, job_id, task_id, sage_bank1[i]["Name"]))

            elif sage_bank1[i]["PaymentMethod"] == 3 :
                _id = sage_bank1[i]["_id"]
                QuerySet2 = {}

                QuerySet2["AccountType"] =2
                QuerySet2["BankAccountStatus"] = 1
                EFT = {}
                EFT['AccountName'] = sage_bank1[i]["Name"][0:15].replace(":","-")
                # account_str = str(sage_bank1[i]["ID"])
                # if len(account_str) ==5:
                #     EFT['EFT1']= '0' + account_str
                # elif len(account_str) ==4:
                #     EFT['EFT1']= '00' + account_str
                # elif len(account_str) ==3:
                #     EFT['EFT1']= '000' + account_str
                # elif len(account_str) ==2:
                #     EFT['EFT1']= '0000' + account_str
                
                if sage_bank1[i]["AccountNumber"] not in ["",None]:
                    EFT['EFT2'] = sage_bank1[i]["AccountNumber"]
                    if "BranchNumber" in sage_bank1[i] and sage_bank1[i]["BranchNumber"] != "":
                        split_branchnumber=sage_bank1[i]["BranchNumber"].replace("-","")
                        EFT['EFT1']=split_branchnumber

                    else:
                        EFT['EFT1']="000000"

    
                    
                BulkElectronicPaymentSettings = {}
                BulkElectronicPaymentSettings['AccountName'] = sage_bank1[i]["Name"][0:15].replace(":","-")
                QuerySet2["BulkElectronicPaymentSettings"] = BulkElectronicPaymentSettings
                QuerySet2["EFT"] = EFT
                QuerySet2["Description"] = sage_bank1[i]["Name"]

                payload = json.dumps(QuerySet2)

                asyncio.run(post_data_in_reckon(url2, post_headers, payload,
                            sage_bank, _id, job_id, task_id, sage_bank1[i]["Name"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)