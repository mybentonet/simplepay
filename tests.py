"""Run tests calling the api to ensure compliance. """
import datetime
import argparse
import simplepay

API_KEY = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', help='The API key to make requests against', required=True)
    args = parser.parse_args()

    pay = simplepay.SimplePay(args.key)

    clients = pay.get_clients()

    if not len(clients):
        raise RuntimeError("Need at least one client to test with")

    employees = pay.get_employees(clients[0]['id'])

    if not len(employees):
        raise RuntimeError("Need at least one employee to test with")

    payslips = pay.get_payslips(employees[0]['id'])

    if not len(payslips):
        raise RuntimeError("Need at least one payslip for employee %s to test with" % employees[0]['id'])

    # Test that we don't get any exceptions calling any of these methods

    if not len(pay.get_leave_types(clients[0]['id']).items()):
        raise RuntimeError("No leave types")

    if not len(pay.get_leave_balances(clients[0]['id'], employees[0]['id'], datetime.datetime.now())):
        raise RuntimeError("No leave balances")

    for employee in employees:
        if len(pay.get_leave_days(employee['id'])):
            break
    else:
        raise RuntimeError("Employee does not have any leave days")

    if 'first_name' not in pay.get_employee(employees[0]['id']):
        raise RuntimeError("Employee does not have first_name field")

    if 'income' not in pay.get_payslip(payslips[0]['id']):
        raise RuntimeError("Payslip does not have income field")

    if not len(pay.get_payslip_pdf(payslips[0]['id'])):
        raise RuntimeError("Payslip pdf invalid")

    # Intentionally cause exceptions
    try:
        pay.get_employee(1)
    except simplepay.NotFound:
        pass

    pay = simplepay.SimplePay('1')
    try:
        pay.get_clients()
    except simplepay.SimplePayException:
        pass
