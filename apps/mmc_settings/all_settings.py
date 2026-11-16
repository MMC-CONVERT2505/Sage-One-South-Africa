from sqlalchemy.orm import aliased

from apps import db
from apps.home.models import Jobs, Tool

from apps.mmc_settings.get_reckon import get_reckon_settings,get_reckon_settings_v2
from apps.mmc_settings.post_reckon import post_reckon_settings,post_reckon_settings_v2
from apps.mmc_settings.get_sage_one import get_sageone_settings
from apps.myconstant import *
from apps.util.log_file import log_config


def get_settings_reckon(job_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside get_settings_reckon")
    """get_settings reckon"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label("input_tool"),
                                                     output_data.account_type.label("output_tool"), ).join(input_data,
                                                                                                           Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == RECKON:
        payload, base_url, headers, book, post_headers, get_headers = get_reckon_settings(
            job_id)
        return payload, base_url, headers, book, post_headers, get_headers

    if output_tool == RECKON:
        payload, base_url, headers, book, post_headers, get_headers = post_reckon_settings(
            job_id)
        return payload, base_url, headers, book, post_headers, get_headers
    

def get_settings_reckon_v2(job_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside get_settings_reckon")
    """get_settings reckon"""

    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(Jobs, input_data.account_type.label("input_tool"),
                                                     output_data.account_type.label("output_tool"), ).join(input_data,
                                                                                                           Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == RECKON:
        payload, base_url, headers, book, post_headers, get_headers = get_reckon_settings_v2(
            job_id)
        return payload, base_url, headers, book, post_headers, get_headers

    if output_tool == RECKON:
        payload, base_url, headers, book, post_headers, get_headers = post_reckon_settings_v2(
            job_id)
        return payload, base_url, headers, book, post_headers, get_headers




def get_settings_sageone(job_id):
    logging = log_config(job_id)
    logging.info(f"{job_id} inside get_settings_sageone")
    input_data = aliased(Tool)
    output_data = aliased(Tool)

    jobs, input_tool, output_tool = db.session.query(
        Jobs,
        input_data.account_type.label("input_tool"),
        output_data.account_type.label("output_tool")).join(input_data, Jobs.input_account_id == input_data.id).join(
        output_data, Jobs.output_account_id == output_data.id).filter(Jobs.id == job_id).first()

    if input_tool == SAGEONE:
        payload, headers, api_key_data, company_id_data = get_sageone_settings(
            job_id)
        return payload, headers, api_key_data, company_id_data
