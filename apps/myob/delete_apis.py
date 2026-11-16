from apps.util.db_mongo import get_mongodb_database
from apps.util.log_file import log_config

def delete_coa(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_coa")
    dbname = get_mongodb_database()
    dbname["QBO_COA"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in QBO_COA")


def delete_supplier(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_supplier")
    dbname = get_mongodb_database()
    dbname["QBO_Supplier"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in QBO_Supplier")


def delete_customer(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_customer")
    dbname = get_mongodb_database()
    dbname["QBO_Customer"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in QBO_Customer")
    

def delete_item(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_item")
    dbname = get_mongodb_database()
    dbname["QBO_Item"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in QBO_Item")


def delete_chart_of_account(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_chart_of_account")
    dbname = get_mongodb_database()
    dbname["chart_of_account"].drop()
    logging.info(f"{job_id} drop the chart_of_account ")


def delete_excel_reckon_invoice(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_excel_reckon_invoice")
    dbname = get_mongodb_database()
    dbname["excel_reckon_invoice"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in excel_reckon_invoice")


def delete_reckon_item(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_reckon_item")
    dbname = get_mongodb_database()
    dbname["reckon_item"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in reckon_item")


def delete_excel_reckon_bill(job_id,task_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside delete_excel_reckon_bill")
    dbname = get_mongodb_database()
    dbname["excel_reckon_bill"].delete_many({'job_id':job_id})
    logging.info(f"{job_id} deleted many data in excel_reckon_bill")
