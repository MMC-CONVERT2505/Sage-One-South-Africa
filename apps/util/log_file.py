import logging
import os


def log_config(job_id):
    os.makedirs("apps/static/logfile", exist_ok=True)
    file_name = f"apps/static/logfile/SageOne_To_ReckonOne_{job_id}.log"

    logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()  
    return logger

def log_config_job_creation(id):
    os.makedirs("apps/static/logfilejob", exist_ok=True)
    file_name = f"apps/static/logfilejob/SageOne_To_ReckonOne_{id}.log"

    logging.basicConfig(filename=file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()  
    return logger
