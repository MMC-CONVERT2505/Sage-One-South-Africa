import json
import requests
import traceback
from apps.mmc_settings.all_settings import *
from apps.util.db_mongo import get_mongodb_database
from apps.util.qbo_util import post_data_in_reckon
import asyncio
from apps.util.qbo_util import instance_check
from apps.util.log_file import log_config

def add_reckon_item(job_id, task_id):
    logging = log_config(job_id)
    try:
        logging.info(f"{job_id} inside add_reckon_item")
        dbname = get_mongodb_database()
        payload, base_url, headers, book, post_headers, get_headers = get_settings_reckon(
            job_id)

        url = f"{base_url}/items"

        sage_item = dbname['sage_item']

        x = sage_item.find({"job_id": job_id,"is_pushed":0})
        sage_item1 = []
        for k in x:
            sage_item1.append(k)


        sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        sage_tax = []
        for p01 in sage_tax1:
            sage_tax.append(p01)


        reckon_coa = dbname["reckon_coa"].find({"job_id": job_id})
        reckon_coa1 = []
        for p1 in reckon_coa:
            reckon_coa1.append(p1)

        # sage_tax1 = dbname["sage_tax"].find({"job_id": job_id})
        # sage_tax = []
        # for p01 in sage_tax1:
        #     sage_tax.append(p01)


        

        taxcode_reckon1 = dbname["taxcode_reckon"].find({"job_id": job_id})
        taxcode_reckon = []
        for p1 in taxcode_reckon1:
            taxcode_reckon.append(p1)

        for i in range(0, len(sage_item1)):
            _id=sage_item1[i]["_id"]
            ItemQuerySet1 = {}
            ItemQuerySet1["Name"] = sage_item1[i].get("Code", None)
            ItemQuerySet1["ItemCode"] = sage_item1[i].get("ID", None)
            ItemQuerySet1["Email"] = sage_item1[i].get("Email", None)
            ItemQuerySet1["ItemStatus"] = 1

            if sage_item1[i]["Physical"] == True:
                ItemQuerySet1["ItemType"] = 1
            else:
                ItemQuerySet1["ItemType"] = 2

            if "Description" in sage_item1[i]:

                ItemQuerySet1["SaleDescription"] =sage_item1[i]["Description"]
                ItemQuerySet1["PurchaseDescription"] =sage_item1[i]["Description"]
            else:
                ItemQuerySet1["SaleDescription"]=None
                ItemQuerySet1["PurchaseDescription"] =None

                    

            for n in range(0, len(reckon_coa1)):

                if sage_item1[i]["ItemReportingGroupSalesName"].lower().strip().replace(":", " ") == reckon_coa1[n]["Name"].lower().strip().replace(":", " "):
                    ItemQuerySet1["SaleCategoryId"] = reckon_coa1[n]["Id"]
                    ItemQuerySet1["IsSold"] = True
                    ItemQuerySet1["SalePrice"]= sage_item1[i]["PriceExclusive"]
        
                    break
                else:
                    ItemQuerySet1["SaleCategoryId"] = None
                    ItemQuerySet1["IsSold"] = False
                    ItemQuerySet1["SalePrice"]=0
                    
            for o in range(0,len(reckon_coa1)):

                if sage_item1[i]["ItemReportingGroupPurchasesName"].lower().strip().replace(":", " ") == reckon_coa1[o]["Name"].lower().strip().replace(":", " "):

                    ItemQuerySet1["PurchaseCategoryId"] = reckon_coa1[o]["Id"]
                    ItemQuerySet1["IsBought"] = True
                    ItemQuerySet1["PurchasePrice"]= sage_item1[i]["PriceExclusive"]
                    break

                else:

                    ItemQuerySet1["PurchaseCategoryId"] = None
                    ItemQuerySet1["IsBought"] = False
                    ItemQuerySet1["PurchasePrice"]=0

            sale_tax = None
           
            for t in range(0,len(sage_tax)):
                for m in range(0, len(taxcode_reckon)):
                    if "TaxTypeIdSales" in sage_item1[i]:
                        if sage_item1[i]["TaxTypeIdSales"]==0:
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                        elif sage_item1[i]["TaxTypeIdSales"] == sage_tax[t]["ID"]:
                            if sage_tax[t]["Name"] in  ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Manual Tax":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break

                            elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "GST 0%":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                if taxcode_reckon[m]["Name"] == 'INP':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    sale_tax = taxcode_reckon[m]['ID']
                                    break     

                    else:
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            sale_tax = taxcode_reckon[m]['ID']
                    
                    ItemQuerySet1["SaleTaxId"] = sale_tax
                   

                
            purchase_tax = None
            for t in range(0,len(sage_tax)):
                for m in range(0, len(taxcode_reckon)):
                    if "TaxTypeIdPurchases" in sage_item1[i]:
                        
                        if sage_item1[i]["TaxTypeIdPurchases"]==0:
                            if taxcode_reckon[m]["Name"] == 'NO TAX':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break

                        elif sage_item1[i]["TaxTypeIdPurchases"] == sage_tax[t]["ID"]:
                            if sage_tax[t]["Name"] in  ["Manual Tax (Capital Goods)","GST ON SALES  10%","GST On Sales","GST on sales ","GST on Sales","Gst on sales"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Manual Tax":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            
                            elif sage_tax[t]["Name"] == "Goods and Services Tax":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] in  ["GST 10%","GST 10% - Purchases","GST on Purchases","GST Purchase 10%"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "GST 0%":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Export Sales - GST Free":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Input Taxed Sales and Supplies":
                                if taxcode_reckon[m]["Name"] == 'INP':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] in ["Capital Purchases","Non Capital Purchases 10%","non capital purchases INP","capital acquisitions CAP","Non Cap Purchase - GST10%","Non capital purchase-GST","Capital acquisitions-GST","Non capital purchase-GST","Purchases GST 10%","Purchases 10%","INP","GST","Non capital purchase","Non capital purchase 10%","Non-capital purchase-GST","Non capital purchases 10%"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == "Other GST - Free Sales":
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                                
                            elif sage_tax[t]["Name"] == ["Purchases - GST Free","GST free capital acquisitions FCA","GST free other acquisitions FOA","Capital acquisitions-Free GST","Purchases-GST Free"]:
                                if taxcode_reckon[m]["Name"] == 'FRE':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] in  ["Non-Capital Purchases","Non capital purchases ","Non capital purchases","NON Capital Purchases","Non Capital Purchases - incl GST","Non-capital purchases (INP)","Non-Capital Purchases - with GST","Non-Capital Purchase inc GST"]:
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break
                            
                            elif sage_tax[t]["Name"] == "Estimated Purchases - Private Use":
                                if taxcode_reckon[m]["Name"] == 'GST':
                                    purchase_tax = taxcode_reckon[m]['ID']
                                    break     
                            

                    else:
                        if taxcode_reckon[m]["Name"] == 'NO TAX':
                            purchase_tax = taxcode_reckon[m]['ID']
                            
                    
                    ItemQuerySet1["PurchaseTaxId"] = purchase_tax

           
            
            if ItemQuerySet1["IsSold"]== True and ItemQuerySet1["IsBought"] == True:
                ItemQuerySet1["SoldOrPurchased"]=3
                

            elif  ItemQuerySet1["IsSold"]== True:
                ItemQuerySet1["SoldOrPurchased"]=1
                

            elif ItemQuerySet1["IsBought"] == True:
                ItemQuerySet1["SoldOrPurchased"]=2
                
            
            payload = json.dumps(ItemQuerySet1)
            asyncio.run(post_data_in_reckon(url, post_headers, payload, sage_item,
                                            _id, job_id, task_id, sage_item1[i]["Code"]))


    except Exception as ex:
        traceback.print_exc()
        logging.error(ex, exc_info=True)
