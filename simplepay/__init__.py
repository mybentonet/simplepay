"""
https://github.com/cstranex/simplepay
"""
# Copyright 2019 Chris Stranex <chris@stranex.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from typing import List, Dict, Tuple, Any
import json
import datetime
from decimal import Decimal
from requests import Request, Session, Response


__version__ = '0.1b'


class SimplePay:
    """Create a new API instance to make requests with.

    :param api_key: An API key generated on simplepay.co.za
    """

    _URL = "https://www.simplepay.co.za/api/v1"

    def __init__(self, api_key: str):
        self.key = api_key

    def request(self, resource='/', method='GET', *args, **kwargs) -> Response:
        """Return a request session with correct headers set.

        :param method: HTTP Method to use
        :param resource: The API endpoint to request. Must begin with a slash
        :param args: Arguments that are passed directly to the Request object
        :returns: A response object
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        req = Request(method, self._URL + resource, *args, **kwargs)
        req.headers['Authorization'] = self.key
        req.headers['Content-type'] = 'application/json'

        session = Session()
        response = session.send(req.prepare())
        if response.status_code == 404:
            try:
                message = response.json()['message']
            except json.decoder.JSONDecodeError:
                message = response.text
            raise NotFound(message)
        elif not response.ok:
            try:
                message = response.json()['message']
            except json.decoder.JSONDecodeError:
                message = response.text
            raise SimplePayException(message)

        return response

    def get_clients(self) -> List[Dict[str, Any]]:
        """Retrieve a list of clients
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-clients

        :returns: A list of clients
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/clients')
        clients = []
        for client in resp.json():
            clients.append(client['client'])
        return clients

    def get_employees(self, client_id: int) -> List[Dict[str, Any]]:
        """Retrieve a list of employees for a given client id
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-employees

        :param client_id: A valid client id
        :returns: A list of Employees
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/clients/{}/employees'.format(client_id))
        employees = []
        for employee in resp.json():
            employees.append(employee['employee'])
        return employees

    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Retrieve employee information for a given employee id
        See: https://www.simplepay.co.za/api-docs/#get-a-specific-employee

        :param employee_id: A valid employee id
        :returns: Employee information
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/employees/{}'.format(employee_id))
        return resp.json()['employee']

    def get_leave_types(self, client_id: int) -> Dict[str, str]:
        """Get a list of leave types
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-available-leave-types

        :param client_id: A valid client id
        :returns: A dictionary mapping leave id types to names
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/clients/{}/leave_types'.format(client_id))
        return resp.json()

    def get_leave_balances(self, client_id: int, employee_id: int, date: datetime.date) -> List[
        Tuple[str, str, Decimal]
    ]:
        """Retrieve a list of leave balances for the given employee.
        See: https://www.simplepay.co.za/api-docs/#leave

        :param client_id: A valid client id
        :param employee_id: The employee id to retrieve the balances for
        :param date: The date at which to calculate the leave balances
        :returns: A list of tuples in the format: (Leave Name, Leave Id, Balance)
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """

        leave_types = self.get_leave_types(client_id)
        leave_balances = []

        resp = self.request('/employees/{}/leave_balances?date={}'.format(employee_id, date.strftime('%Y-%m-%d')))
        for _id, _balance in resp.json().items():
            leave_balances.append((leave_types[_id], _id, _balance))
        return leave_balances

    def get_leave_days(self, employee_id: str) -> List:
        """Get a list of leave dates for a specific employee
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-leave-days-for-an-employee

        :param employee_id: The employee id to return the leave days for
        :returns: a List of leave entries
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        leave = []
        resp = self.request('/employees/{}/leave_days'.format(employee_id))
        for _item in resp.json():
            leave.append(_item[0])
        return leave

    def get_payslips(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of payslips for an employee
        See: https://www.simplepay.co.za/api-docs/#payslips

        :param employee_id: The employee id to return the payslip data for
        :returns: A list of payslips
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/employees/{}/payslips'.format(employee_id))
        payslips = []
        for payslip in resp.json():
            payslips.append(payslip)
        return payslips

    def get_payslip(self, payslip_id: str) -> Dict[str, Any]:
        """Get a specific payslip
        See: https://www.simplepay.co.za/api-docs/#get-a-a-specific-payslip-for-an-employee

        :param payslip_id: A payslip id
        :returns: A dict containing the payslip information
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/payslips/{}'.format(payslip_id))
        return resp.json()

    def get_payslip_pdf(self, payslip_id: str) -> bytes:
        """Get a payslip PDF
        See: https://www.simplepay.co.za/api-docs/#get-a-a-specific-payslip-for-an-employee

        :param payslip_id: A payslip id
        :returns: The PDF document in bytes
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/payslips/{}.pdf'.format(payslip_id))
        return resp.content


class SimplePayException(Exception):
    """Raised when a resource could not be retrieved"""
    pass


class NotFound(SimplePayException):
    """Raised when a resource requested does not exist or cannot be accessed by the api key"""

