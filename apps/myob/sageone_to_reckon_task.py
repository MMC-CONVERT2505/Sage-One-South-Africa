from apps.home.data_util import update_task_execution_status, write_task_execution_step
from apps.home.models import Task
from apps.sage_one.sageone_reader.get_account import  get_coa
from apps.sage_one.sageone_reader.get_customer import get_customer
from apps.sage_one.sageone_reader.get_supplier import get_supplier
from apps.sage_one.sageone_reader.get_item import get_item
from apps.sage_one.sageone_reader.get_bank import get_bank
from apps.sage_one.sageone_reader.get_invoice import get_invoice
from apps.sage_one.sageone_reader.get_invoice_payment import get_invoice_payment

from apps.sage_one.sageone_reader.get_all_invoice_payment import get_all_invoice_payment_data
from apps.sage_one.sageone_reader.get_all_spend_money import get_all_spend_moeny_data
from apps.sage_one.sageone_reader.get_all_received_money import get_all_received_money_data
from apps.sage_one.sageone_reader.get_all_bill import get_all_bill_data
from apps.sage_one.sageone_reader.get_all_invoice import get_all_invoice_data
from apps.sage_one.sageone_reader.get_all_coa import get_all_coa_data
from apps.sage_one.sageone_reader.get_all_customer import get_all_customer_data
from apps.sage_one.sageone_reader.get_all_supplier import get_all_supplier_data
from apps.sage_one.sageone_reader.get_all_journal import get_all_journal_data
from apps.sage_one.sageone_reader.get_all_bank import get_all_bank_data
from apps.sage_one.sageone_reader.get_all_invoice_creditnote import get_all_invoice_creditnote_data
from apps.sage_one.sageone_reader.get_all_bank_transfer import get_all_bank_transfer_data

from apps.sage_one.sageone_reader.get_all_bill_vendorcredit import get_all_bill_vendorcredit_data

from apps.sage_one.sageone_reader.get_all_open_ar import get_all_open_ar_data

from apps.sage_one.sageone_reader.get_all_open_ap import get_all_open_ap_data 

from apps.sage_one.sageone_reader.get_all_open_trialBalance import get_all_trial_balance_data
from apps.sage_one.sageone_reader.get_all_close_trialBalance import get_all_close_trial_balance_data

from apps.sage_one.sageone_reader.get_all_customer_adjustment import get_all_customer_adjustment_data
from apps.sage_one.sageone_reader.get_all_supplier_adjustment import get_all_supplier_adjustment_data

from apps.sage_one.sageone_reader.get_all_write_off import get_all_customer_write_off_data


from apps.sage_one.sageone_reader.get_all_bill_payment import get_all_bill_payment_data
from apps.sage_one.sageone_reader.get_all_item import get_all_item_data
from apps.sage_one.sageone_reader.get_all_bill_allocation import get_all_bill_allocation_data
from apps.sage_one.sageone_reader.get_all_invoice_allocation import get_all_invoice_allocation_data
from apps.sage_one.sageone_reader.get_all_qbo_allocation import get_all_qbo_invoice_allocation_data, get_all_qbo_bill_allocation_data
from apps.sage_one.sageone_reader.allocation_fetcher import fetch_allocation_sources, AllocationFetchError


def run_allocation_fetch(job_id, task, side, task_type):
    """Allocation ke liye SageOne data laata hai; adhoora rahe to task ko failed (0) mark karta hai."""
    step_name = f"Reading {side} allocation data from sageone "
    update_task_execution_status(task.id, status=2, task_type=task_type)
    write_task_execution_step(task.id, status=2, step=step_name)
    try:
        fetch_allocation_sources(job_id, side)
    except AllocationFetchError as ex:
        write_task_execution_step(task.id, status=0, step=step_name, error=str(ex)[:1000])
        update_task_execution_status(task.id, status=0, task_type=task_type)
        return False
    write_task_execution_step(task.id, status=1, step=step_name)
    if task_type == "read":
        update_task_execution_status(task.id, status=1, task_type=task_type)
    return True


def run_allocation_write(job_id, task, side, build_file):
    """Retry par bhi pehle bacha data laata hai, phir allocation file banata hai."""
    if not run_allocation_fetch(job_id, task, side, "write"):
        return
    step_name = f"write all {side} allocation data sageone "
    write_task_execution_step(task.id, status=2, step=step_name)
    build_file(job_id, task.id)
    write_task_execution_step(task.id, status=1, step=step_name)
    update_task_execution_status(task.id, status=1, task_type="write")
from apps.sage_one.sageone_reader.get_all_sage_tax import get_all_tax_data

from apps.sage_one.sageone_reader.get_bill_payment import get_bill_payment
from apps.sage_one.sageone_reader.get_Allocation import get_allocation
from apps.sage_one.sageone_reader.get_bank_transaction import get_bank_transaction
from apps.sage_one.sageone_reader.get_credit_note import get_credit_note
from apps.sage_one.sageone_reader.get_bill import get_bill
from apps.sage_one.sageone_reader.get_vendorcredit import get_vendorcredit
from apps.sage_one.sageone_reader.get_manual_journal import get_manual_journal
from apps.sage_one.sageone_reader.get_spend_money import get_spend_money, get_spend_money_contact, add_sage_spend_supplier
from apps.sage_one.sageone_reader.get_sage_tax import get_sage_tax
from apps.sage_one.sageone_reader.get_sage_customer_ageing import get_sage_customer_ageing

from apps.sage_one.reckon_data_reader.Get_reckon_report_trial_balance import get_reckon_report_trial_balance
from apps.sage_one.reckon_data_reader.Get_reckon_report_trial_balance_second import get_reckon_report_trial_balance_second_years

from apps.sage_one.sageone_reader.get_sage_report_trial_balance import get_sage_report_trial_balance
from apps.sage_one.sageone_reader.get_sage_report_trial_balance_current import get_sage_report_trial_balance_current


from apps.sage_one.sageone_reader.get_sage_trial_balance import get_sage_trial_balance,get_sage_close_trial_balance

from apps.sage_one.sageone_reader.get_sage_supplier_ageing import get_sage_supplier_ageing
from apps.sage_one.sageone_reader.get_receive_money import get_receive_money,get_receive_money_contact,add_sage_receive_customer,get_common_contact,get_common_contact_customer
from apps.sage_one.sageone_reader.get_bank_transfer import get_bank_transfer
from  apps.sage_one.sageone_reader.get_customer_adjustment import get_customer_adjustment
from apps.sage_one.sageone_reader.get_supplier_adjustment import get_supplier_adjustment
from apps.sage_one.sageone_reader.get_customer_write_off import get_customer_write_off
from apps.sage_one.sageone_reader.get_tax_adjustment import get_tax_adjustment
from apps.reckon_one.excel_reader.reckon_tax import get_reckon_taxcode
from apps.sage_one.reckon_data_reader.Get_invoice import get_reckon_invoice,get_reckon_invoice_excel,get_reckon_invoice_creditnote_excel,get_reckon_invoice_payment_excel
from apps.sage_one.reckon_data_reader.Get_bill import get_reckon_bill,get_reckon_bill_excel,get_reckon_bill_vendorcredit_excel,get_reckon_bill_payment_excel
from apps.sage_one.reckon_data_reader.Get_Reckon_Tax import get_reckon_taxcode_excel
from apps.reckon_one.excel_reader.vendorcredit_template import get_reckon_vendorcredit_template
from apps.reckon_one.excel_reader.chart_of_account import get_reckon_chart_of_account,get_reckon_chart_of_account_excel
from apps.sage_one.reckon_data_reader.Get_reckon_trial_balance import get_reckon_trial_balance
from apps.sage_one.reckon_data_reader.Get_customer import get_reckon_customer,get_reckon_customer_data
from apps.sage_one.reckon_data_reader.Get_supplier import get_reckon_supplier,get_reckon_common_customer,get_reckon_common_supplier
from apps.sage_one.reckon_data_reader.Get_Item import get_reckon_item,get_reckon_item_excel,get_reckon_item_history
from apps.sage_one.reckon_data_reader.Get_project import get_reckon_projects
from apps.sage_one.reckon_data_reader.Get_bank_account import get_reckon_bank_account




from apps.sage_one.reckon_one_writer.add_chart_of_account_reckon import add_reckon_chart_of_account
from apps.sage_one.reckon_one_writer.add_default_chart_of_account_reckon import add_reckon_default_chart_of_account
from apps.sage_one.reckon_one_writer.add_customer_reckon import add_reckon_customer, add_reckon_default_customer,update_reckon_customer,update_reckon_supplier
from apps.sage_one.reckon_one_writer.add_supplier_reckon import add_reckon_supplier, add_reckon_default_supplier
from apps.sage_one.reckon_one_writer.add_item_reckon import add_reckon_item
from apps.sage_one.reckon_one_writer.add_bank_account_reckon import add_reckon_bank_account
from apps.sage_one.reckon_one_writer.add_invoice_reckon import add_sage_invoice
from apps.sage_one.reckon_one_writer.add_invoice_credit_note_reckon import add_invoice_credit_note
from apps.sage_one.reckon_one_writer.add_invoice_payment_reckon import add_invoice_payment
from apps.sage_one.reckon_one_writer.add_bill_payment_reckon import add_bill_payment
from apps.sage_one.reckon_one_writer.add_bill_reckon import add_bill_in_reckon
from apps.sage_one.reckon_one_writer.add_bill_vendorcredit_reckon import add_bill_vendorcredit_reckon
from apps.sage_one.reckon_one_writer.add_journal_reckon import add_journal_reckon
from apps.sage_one.reckon_one_writer.add_trial_balance_journal_reckon import add_trial_balance_journal_reckon
from apps.sage_one.reckon_one_writer.add_reckon_reverse_trial_balance_journal import add_reckon_reverse_trial_balance_journal
from apps.sage_one.reckon_one_writer.add_spend_money import add_spend_money

from apps.sage_one.reckon_one_writer.add_spend_money_as_tax_payment import add_tax_payment_as_spend_money
from apps.sage_one.reckon_one_writer.add_receive_money import add_receive_money
from  apps.sage_one.reckon_one_writer.add_bank_transfer import add_reckon_bank_transfer
from apps.sage_one.reckon_one_writer.add_customer_adjustment import add_journal_as_a_customer_adjustment
from apps.sage_one.reckon_one_writer.add_supplier_adjustment import add_journal_as_a_supplier_adjustment
from apps.sage_one.reckon_one_writer.add_customer_write_off import add_journal_as_a_customer_write_off
from apps.sage_one.reckon_one_writer.add_tax_adjustment import add_journal_as_a_tax_adjustment
from apps.sage_one.reckon_one_writer.add_ar_invoice_reckon import add_customer_ageing_type
from apps.sage_one.reckon_one_writer.add_ap_reckon import add_supplier_ageing_type
from apps.sage_one.sageone_reader.match_trial_balance_previous_year import trial_balance_previous_report,trial_balance_current_report

from apps.util.db_mongo import get_mongodb_database
class SageoneToReckonone(object):
    @staticmethod
    def read_data(job_id, task):
        print("read data--------")
        print(task.function_name,"task function name")
        step_name = None
        try:
            
            if "Chart of account" == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from  reckon taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from sageone chart_of_account"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from sageone bank"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Customer" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            
            if "Supplier" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading supplier data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "Item"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Invoice"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading invoice data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Invoice Payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading invoice payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                # get_reckon_invoice(job_id, task.id)
                get_invoice_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading allocation data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_allocation(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank transaction data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank_transaction(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading invoice data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "Reckon_coa"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
            
                step_name = "Reading coa data from Reckon "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            
            if "Reckon_item"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
            
                step_name = "Reading Item  data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)

                get_reckon_item_history(job_id, task.id)

                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            

            if "Reckon_customer"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
            
                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Reckon_supplier"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
            
                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            
            if "Reckon_Invoice"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                
                

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)

                get_reckon_projects(job_id, task.id)

                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading Invoice data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_invoice_excel(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Reckon_Invoice_creditnote"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading Invoice creditnote data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_invoice_creditnote_excel(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "Reckon_bill"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bill_excel(job_id, task.id)
                get_reckon_projects(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Reckon_Taxcode"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading Tax data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode_excel(job_id, task.id)

                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")


            
            if "Reckon_bill_vendorcredit"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bill_vendorcredit_excel(job_id, task.id)

                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "Reckon_bill_payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill payment data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bill_payment_excel(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Reckon_invoice_payment" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading invoice payment data from Reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_invoice_payment_excel(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

                

            

            if "All Invoice Payment Data"  == task.function_name:

                update_task_execution_status(


                    task.id, status=2, task_type="read")


                step_name = "Reading bill payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading allocation data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_allocation(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

               
                step_name = "Reading bill data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading invoice payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading allocation data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_allocation(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading invoice data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "All Coa Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading coa data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")


            if "All Customer Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "All Supplier Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading supplier data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "All Journal Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading journal data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_manual_journal(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")




            if "All Spend Money Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading spend money data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_spend_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")  

            
            if "All Receive Money Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading receive money data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_receive_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
                update_task_execution_status(
                    task.id, status=1, task_type="read")  


            if "All Invoice Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading invoice  data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")  


            if "All Bill Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading bill data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")  


            if "All Item Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading Item data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")  


            

            if "All Tax Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")

                step_name = "Reading Tax data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")  



                
            if "All Bill Payment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading allocation data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_allocation(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

               
                step_name = "Reading bill data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


            
               
                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
                

            if "Bill Payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading supplier data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading allocation data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_allocation(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank transaction data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank_transaction(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bill data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
           
           
                

            if "Invoice CreditNote"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading invoice creditnote data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_credit_note(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                


                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "Spend Money"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading spend money data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_spend_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "get_spend_money_contact"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_spend_money_contact(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading  supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "get_common_contact_customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_common_contact_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "get_receive_common_supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_common_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Update_comman_supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                update_reckon_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Add spend money contact as supplier"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_sage_spend_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading sageone tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "Reading bank accounts data from reckon one & sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from r sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone  "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from  sage "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Receive Money"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading receive money data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_receive_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "get_receive_money_contact"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_receive_money_contact(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading  supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "get_common_contact"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_common_contact(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "get_receive_common_contact"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_common_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Update_comman_contact"
                write_task_execution_step(task.id, status=2, step=step_name)
                update_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Add receive money contact as customer"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_sage_receive_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from reckon one "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from  sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sage "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                step_name = "Reading chart of account data from reckonone  "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Bill"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading templet data from reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_vendorcredit_template(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Bank Transfer"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bank transfer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank_transfer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")


            if "Tax Payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bank transfer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank_transfer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading sageone tax"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading  supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from reckon one & sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from r sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone  "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from  sage "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_tax(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
              
                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
                
            if "Bill VendorCredit"   == task.function_name:
              
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading bill_vendorcredit data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_vendorcredit(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading templet data from reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_vendorcredit_template(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                



                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Journal"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading journal data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_manual_journal(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Trial Balance"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading journal data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_trial_balance(job_id,task.id)
                get_reckon_trial_balance(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                update_task_execution_status(
                    task.id, status=1, task_type="read")



            if "Customer Adjustments" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading customer adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from  reckon taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from sageone chart_of_account"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            
            if "Supplier Adjustments" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading supplier adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from  reckon taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from sageone chart_of_account"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                

                step_name = "Reading supplier data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            
            if "Customer Write Off" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading customer write off data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer_write_off(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from  reckon taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from reckon chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from sageone chart_of_account"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "Tax Adjustment" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading tax adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_tax_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from reckon chart of account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from sageone chart_of_account"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
                step_name = "Reading customer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Open AR"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                

                step_name = "Reading customer  ageing data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_customer_ageing(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading invoice payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_invoice_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from reckon one "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from  sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                                
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                
            if "Open AP"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading Supplier ageing data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_supplier_ageing(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading templet data from reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_vendorcredit_template(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

               
                step_name = "Reading Bill payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bill_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)


                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from reckon one "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank accounts data from  sage"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                                
                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "Report" == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_coa(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading data from sageone "
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_sage_report_trial_balance(job_id,task.id)
                get_sage_report_trial_balance_current(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "Reading data from  reckon taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                get_reckon_report_trial_balance(job_id,task.id)
                get_reckon_report_trial_balance_second_years(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")

            if "All Bank Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Read Bank data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "All Bank Transfer Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Read Bank Transfer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_bank_transfer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            

            if "All Invoice CreditNote Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Read invoice CreditNote data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_credit_note(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            
            if "All Bill VendorCredite Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Read bill vendorcredite data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_vendorcredit(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            
            if "All Open AR Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Read open ar data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_customer_ageing(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "All Open AP Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write open ap data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_supplier_ageing(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "All Open Trial Balance Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write open trial data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_trial_balance(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            

            if "All Close Trial Balance Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write open trial data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_sage_close_trial_balance(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "All Customer Adjustment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write customer adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            
            if "All Supplier Adjustment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write supplier adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_supplier_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
                

            if "All Customer Write Off Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="read")
                
                step_name = "Write customer write off data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_customer_write_off(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="read")
            



            if "All Bill Allocation Data"  == task.function_name:
                run_allocation_fetch(job_id, task, "bill", "read")

            if "All Invoice Allocation Data"  == task.function_name:
                run_allocation_fetch(job_id, task, "invoice", "read")

            if "All QBO Bill Allocation Data"  == task.function_name:
                run_allocation_fetch(job_id, task, "qbo bill", "read")

            if "All QBO Invoice Allocation Data"  == task.function_name:
                run_allocation_fetch(job_id, task, "qbo invoice", "read")

        except Exception as ex:
            print("error display ")
            write_task_execution_step(task.id, status=0, step=step_name)
            update_task_execution_status(
                job_id, task.id, status=0, task_type="read")
            raise ex

    @staticmethod
    def write_data(job_id, task):
        step_name = None
        try:
            dbname = get_mongodb_database()
            if "Chart of account" == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_default_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Write chart_of_account data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Write bank data"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_bank_account(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Customer" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Adding customer data in reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Adding default customer data in reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_default_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Supplier" == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Adding supplier data in reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Adding default supplier data in reckonone"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_default_supplier(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Item"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading data from reckon chart_of_account"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                results = dbname['reckon_coa'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_chart_of_account(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                step_name = "Reading data from reckon tax"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                results = dbname['taxcode_reckon'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_taxcode(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
            
                step_name = "Adding Item data to reckonone"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                add_reckon_item(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Invoice"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write invoice data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_sage_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")


            if "Invoice CreditNote"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_customer'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_supplier'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_coa'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['taxcode_reckon'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_item'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write invoice credit note  data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_invoice_credit_note(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                

            
            if "Bill"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                
                step_name = "write bill data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_bill_in_reckon(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Bill VendorCredit"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_supplier'].count_documents({"job_id": job_id})
                if results == 0:
  
                    get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_coa'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading taxcode data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['taxcode_reckon'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_taxcode(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading item data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_item'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_item(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write bill data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_bill_vendorcredit_reckon(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Journal"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                results = dbname['taxcode_reckon'].count_documents({"job_id": job_id})
                if results == 0:
                
                
                    get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "write journal data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_journal_reckon(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            if "Trial Balance"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading data from  sageone taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                results = dbname['taxcode_reckon'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_sage_tax(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                step_name = "write reckon reverse trial balance journal data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_reverse_trial_balance_journal(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                
                step_name = "write trial balance journal data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_trial_balance_journal_reckon(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
                
            if "Invoice Payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_customer'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_customer(job_id, task.id)
  
                results = dbname['reckon_supplier'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_coa'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_bank_account'].count_documents({"job_id": job_id})
                if results == 0:
               
                    get_reckon_bank_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading invoice data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_invoice'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_invoice(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write invoice data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_invoice_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "All Invoice Payment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                # step_name = "Write bill payment data from sageone "
                # write_task_execution_step(task.id, status=2, step=step_name)
                # get_all_bill_payment_data(job_id, task.id)
                # write_task_execution_step(task.id, status=1, step=step_name)

                

                step_name = "write all invoice payment data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_invoice_payment_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "All Coa Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all coa data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_coa_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                

            if "All Customer Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all customer data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_customer_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "All Supplier Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all supplier data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_supplier_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "All Journal Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all journal data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_journal_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")


            if "All Spend Money Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all spend money data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)

                get_all_spend_moeny_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "All Receive Money Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write all receive money data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_received_money_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")


            if "All Invoice Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")

                step_name = "write all invoice data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)

                get_all_invoice_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")


            if "All Bill Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
            
                step_name = "write all bill data sageone "
                write_task_execution_step(task.id, status=2, step=step_name)

                get_all_bill_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                

            if "All Bill Payment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                
                
                step_name = "Write bill payment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_bill_payment_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            if "All Item Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write Item data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_item_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                
            
            if "All Tax Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")

                step_name = "Write Tax data from sageone"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_tax_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
            
               
                update_task_execution_status(
                    task.id, status=1, task_type="write")  

            
            if "All Bank Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write Bank data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_bank_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            

            if "All Bank Transfer Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write Bank Transfer data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_bank_transfer_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            

            if "All Invoice CreditNote Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write invoice CreditNote data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_invoice_creditnote_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            
            if "All Bill VendorCredite Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write bill vendorcredite data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_bill_vendorcredit_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            
            if "All Open AR Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write open ar data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_open_ar_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            if "All Open AP Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write open ap data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_open_ap_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            if "All Open Trial Balance Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write open trial data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_trial_balance_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                

            
            if "All Close Trial Balance Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write close trial data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_close_trial_balance_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")


            
            if "All Customer Adjustment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write customer adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_customer_adjustment_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            
            if "All Supplier Adjustment Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write supplier adjustment data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_supplier_adjustment_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
                

            if "All Customer Write Off Data"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write customer write off data from sageone "
                write_task_execution_step(task.id, status=2, step=step_name)
                get_all_customer_write_off_data(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            

            if "All Bill Allocation Data"  == task.function_name:
                run_allocation_write(job_id, task, "bill", get_all_bill_allocation_data)

            if "All Invoice Allocation Data"  == task.function_name:
                run_allocation_write(job_id, task, "invoice", get_all_invoice_allocation_data)

            if "All QBO Bill Allocation Data"  == task.function_name:
                run_allocation_write(job_id, task, "qbo bill", get_all_qbo_bill_allocation_data)

            if "All QBO Invoice Allocation Data"  == task.function_name:
                run_allocation_write(job_id, task, "qbo invoice", get_all_qbo_invoice_allocation_data)

            if "Bill Payment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)

                results = dbname['reckon_supplier'].count_documents({"job_id": job_id})
                if results == 0:
                    get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading chart of account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_coa'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_chart_of_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bank account data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_bank_account'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_bank_account(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading bill data from reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                results = dbname['reckon_bill'].count_documents({"job_id": job_id})
                if results == 0:
                
                    get_reckon_bill(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write bill payment data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_bill_payment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            if "Bank Transfer"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                
                step_name = "write bank transfer data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_reckon_bank_transfer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
            

            if "Spend Money"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")


                step_name = "Reading customer data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading  supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write spend money data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_spend_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")   

            if "Tax Payment"  == task.function_name:
                
                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "write tax payment data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_tax_payment_as_spend_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")   



            if "Receive Money"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")

                step_name = "Reading customer  data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_customer(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "Reading  supplier data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                get_reckon_supplier(job_id,task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                step_name = "write receive money data in reckonone "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_receive_money(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write") 
                

            if "Customer Adjustments"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write customer adjustment data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_journal_as_a_customer_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write") 
            
            if "Supplier Adjustments"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write supplier adjustment data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_journal_as_a_supplier_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")

            
            if "Customer Write Off"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write customer write off data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_journal_as_a_customer_write_off(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)
                update_task_execution_status(
                    task.id, status=1, task_type="write") 
                
            
            if "Tax Adjustment"  == task.function_name:

                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Write tax adjustment data from reckon one"
                write_task_execution_step(task.id, status=2, step=step_name)
                add_journal_as_a_tax_adjustment(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write") 

            if "Open AR"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Writing customer ageing data to Reckon  "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_customer_ageing_type(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
               

            if "Open AP"  == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Writing customer ageing data to Reckon  "
                write_task_execution_step(task.id, status=2, step=step_name)
                add_supplier_ageing_type(job_id, task.id)
                write_task_execution_step(task.id, status=1, step=step_name)

                update_task_execution_status(
                    task.id, status=1, task_type="write")
               
            
            if "Report" == task.function_name:
                update_task_execution_status(
                    task.id, status=2, task_type="write")
                
                step_name = "Reading data from both sage and reckon  taxcode"
                write_task_execution_step(
                    task.id, status=2, step=step_name)
                trial_balance_previous_report(job_id,task.id)
                trial_balance_current_report(job_id,task.id)
                write_task_execution_step(
                    task.id, status=1, step=step_name)
                
                update_task_execution_status(
                    task.id, status=1, task_type="write")
               
               

        except Exception as ex:
            write_task_execution_step(task.id, status=0, step=step_name)
            update_task_execution_status(
                job_id, task.id, status=0, task_type="read")
            raise ex
