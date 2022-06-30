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

import asyncio
import logging
import pprint
from typing import List, Dict, Optional, Tuple, Any, Union
import json
from json.decoder import JSONDecodeError
import datetime
from decimal import Decimal
import random
from requests import Request, Session, Response
import uuid


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
            except JSONDecodeError:
                message = response.text
            raise NotFound(message)
        elif not response.ok:
            json = response.json()
            print(f"Response: {response} {response.json()} {response.text}")
            try:
                message = json['message']
                if 'errors' in json:
                    message += str(json['errors'])
            except JSONDecodeError:
                message = response.text
            raise SimplePayException(message)

        return response

    async def request_async(self, resource='/', method='GET', *args, **kwargs) -> Response:
        """Return a request session with correct headers set.

        :param method: HTTP Method to use
        :param resource: The API endpoint to request. Must begin with a slash
        :param args: Arguments that are passed directly to the Request object
        :returns: A response object
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        from aiohttp import ClientSession

        headers = {}
        headers['Authorization'] = self.key
        headers['Content-type'] = 'application/json'

        # WARNING: TODO: HORRIBLE HACK FOR RATE LIMITING BY SIMPLEPAY
        id = uuid.uuid4()
        sleep_time = random.randrange(20, 100) / 100.0
        logging.debug(f"Sleeping {sleep_time} seconds for request ID {id}")
        await asyncio.sleep(sleep_time)
        logging.debug(f"Finished sleeping for request ID {id}")

        async with ClientSession(
            headers = headers,
        ) as client:
            async with client.request(method, self._URL + resource, *args, **kwargs) as response:
                if response.status == 404:
                    logging.debug(f"Handling 404")

                    try:
                        message = await response.json()
                        message = message['message']
                    except JSONDecodeError:
                        message = await response.text
                    raise NotFound(message)
                elif not response.ok:
                    try:
                        json = await response.json()
                    except Exception as e:
                        logging.error(f"Exception {e} {response.text}")
                        raise e

                    print(f"Response: {response} {response.json()} {response.text}")
                    try:
                        message = json['message']
                        if 'errors' in json:
                            message += str(json['errors'])
                    except JSONDecodeError:
                        message = response.text
                    raise SimplePayException(f"Status: {response.status}: {message}")
                response_json = await response.json()
                return response_json

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

    async def get_employee_async(self, employee_id: int) -> Dict[str, Any]:
        """Retrieve employee information for a given employee id
        See: https://www.simplepay.co.za/api-docs/#get-a-specific-employee

        :param employee_id: A valid employee id
        :returns: Employee information
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/employees/{}'.format(employee_id))
        return resp['employee']

    def get_leave_accrual_policies(self, client_id: int, start_date: Union[str, datetime.date], end_date: Union[str, datetime.date], leave_types: list, employee_ids: Optional[list[Union[str, int]]] = None) -> Dict[str, str]:
        """Get a list of leave accumulation policies
        See: https://simplepay.co.za/api-docs/#variance-report

        :param client_id: A valid client id
        :param start_date: Beginning of period to check
        :param end_date: End of period to check
        :param leave_types: Array of SimplePay IDs for leave types
        :param employee_ids: optional list of ids
        :returns: A dictionary mapping leave id types to names

        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        print({
                'start_date': start_date, 
                'end_date': end_date,
                'wave_ids': None,
                'employee_ids': None,
                'leave_types': leave_types,
                'humanize': True})
        resp = self.request('/clients/{}/reports/comparison_leave'.format(client_id),
            method='POST', json={
                'start_date': start_date, 
                'end_date': end_date,
                'wave_ids': None,
                'employee_ids': None,
                'leave_types': leave_types,
                'humanize': False}
        )
        return resp.json()

    async def get_leave_accrual_policies_async(self, client_id: int, start_date: Union[str, datetime.date], end_date: Union[str, datetime.date], leave_types: list, employee_ids: Optional[list[Union[str, int]]] = None) -> Dict[str, str]:
        """Get a list of leave accumulation policies
        See: https://simplepay.co.za/api-docs/#variance-report

        :param client_id: A valid client id
        :param start_date: Beginning of period to check
        :param end_date: End of period to check
        :param leave_types: Array of SimplePay IDs for leave types
        :param employee_ids: optional list of ids
        :returns: A dictionary mapping leave id types to names

        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/clients/{}/reports/comparison_leave'.format(client_id),
            method='POST', json={
                'start_date': start_date, 
                'end_date': end_date,
                'wave_ids': None,
                'employee_ids': None,
                'leave_types': leave_types,
                'humanize': False}
        )
        return resp


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

    async def get_leave_types_async(self, client_id: int) -> Dict[str, str]:
        """Get a list of leave types
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-available-leave-types

        :param client_id: A valid client id
        :returns: A dictionary mapping leave id types to names
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/clients/{}/leave_types'.format(client_id))
        return resp

    def get_leave_balances(self, employee_id: int, date: datetime.date) -> List:
        """Retrieve a list of leave balances for the given employee.
        See: https://www.simplepay.co.za/api-docs/#leave

        :param employee_id: The employee id to retrieve the balances for
        :param date: The date at which to calculate the leave balances
        :returns: A list of dictionaries with keys: (leave_id, balance)
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """

        resp = self.request('/employees/{}/leave_balances?date={}'.format(employee_id, date.strftime('%Y-%m-%d')))
        return [{'leave_id': k, 'balance': v} for (k, v) in resp.json().items()]

    async def get_leave_balances_async(self, employee_id: int, date: datetime.date) -> List:
        """Retrieve a list of leave balances for the given employee.
        See: https://www.simplepay.co.za/api-docs/#leave

        :param employee_id: The employee id to retrieve the balances for
        :param date: The date at which to calculate the leave balances
        :returns: A list of dictionaries with keys: (leave_id, balance)
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """

        resp = await self.request_async('/employees/{}/leave_balances?date={}'.format(employee_id, date.strftime('%Y-%m-%d')))
        return [{'leave_id': k, 'balance': v} for (k, v) in resp.items()]

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

    def get_leave_days_async(self, employee_id: str) -> List:
        """Get a list of leave dates for a specific employee
        See: https://www.simplepay.co.za/api-docs/#get-a-list-of-leave-days-for-an-employee

        :param employee_id: The employee id to return the leave days for
        :returns: a List of leave entries
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        leave = []
        resp = self.request_async('/employees/{}/leave_days'.format(employee_id))
        for _item in resp:
            leave.append(_item[0])
        return leave

    def add_leave_days(self, employee_id: str, type_id: int, leave_days: List[str]) -> Dict:
        """Add new leave days to employee
        See: https://www.simplepay.co.za/api-docs/#create-multiple-new-leave-days

        Note: passes None for hours indicating all days are full days
        
        :param employee_id: The employee id to add leave days to
        :param type_id: Internal SimplePay leave type identifier
        :param leave_days: a list of strings of the format 'YYYY-MM-DD'
        :returns: dictionary message and leave day IDs on success
        '"""
        data = {"dates":
            [{"date": date, "hours": None, "type_id": int(type_id)}
             for date in leave_days]
        }
        resp = self.request('/employees/{}/leave_days/create_multiple'.format(employee_id),
                            method='POST',
                            json=data)
        return resp.json()

    def delete_leave_day(self, leave_day_id: int) -> Dict:
        """Delete existing leave day
        See: https://www.simplepay.co.za/api-docs/#delete-an-existing-leave-day

        :param leave_day_id: The leave day to delete
        :returns: dictionary message on success
        '"""
        resp = self.request('/leave_days/{}'.format(leave_day_id),
                            method='DELETE')
        return resp.json()

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

    async def get_payslips_async(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of payslips for an employee
        See: https://www.simplepay.co.za/api-docs/#payslips

        :param employee_id: The employee id to return the payslip data for
        :returns: A list of payslips
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/employees/{}/payslips'.format(employee_id))
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

    async def get_payslip_async(self, payslip_id: str) -> Dict[str, Any]:
        """Get a specific payslip
        See: https://www.simplepay.co.za/api-docs/#get-a-a-specific-payslip-for-an-employee

        :param payslip_id: A payslip id
        :returns: A dict containing the payslip information
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        response_json = await self.request_async('/payslips/{}'.format(payslip_id))
        return response_json

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

    def get_calculations(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of calculations for an employee
        See: https://www.simplepay.co.za/api-docs/#calcuations

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of calculations
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        return self.request('/employees/{}/calculations'.format(employee_id)).json()

    async def get_calculations_async(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of calculations for an employee
        See: https://www.simplepay.co.za/api-docs/#calcuations

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of calculations
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/employees/{}/calculations'.format(employee_id))
        return resp

    def get_payslip_calculations(self, payslip_id: str) -> List[Dict[str, Any]]:
        """Get a list of calculations for an payslip
        See: https://www.simplepay.co.za/api-docs/#calcuations

        :param payslip_id: The payslip id to return the calculation data for
        :returns: A list of calculations
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        return self.request('/payslips/{}/calculations'.format(payslip_id)).json()

    def get_inherited_calculations(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of inherited calculations for an employee
        See: https://www.simplepay.co.za/api-docs/#inherited-calcuations

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of calculations
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        return self.request('/employees/{}/inherited_calculations'.format(employee_id)).json()

    async def get_inherited_calculations_async(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of inherited calculations for an employee
        See: https://www.simplepay.co.za/api-docs/#inherited-calcuations

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of calculations
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/employees/{}/inherited_calculations'.format(employee_id))
        return resp

    def create_calculation(self, employee_id: str, calculation: dict) -> Dict[str, Any]:
        """Create a new calculation for an employee
        See: https://www.simplepay.co.za/api-docs/#create-update-a-calculation

        :param employee_id: The employee id to return the calculation data for
        :param calculation: Details of new calculation 
        :returns: Response to create
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/employees/{}/leave_days/create_multiple'.format(employee_id),
                            method='POST',
                            json=data)

        return self.request('/employees/{}/inherited_calculations'.format(employee_id)).json()

    def create_payslip_calculation(self, payslip_id: str, calculation: dict) -> Dict[str, Any]:
        """Create a new calculation for an payslip
        See: https://www.simplepay.co.za/api-docs/#create-update-a-calculation

        :param payslip_id: The payslip id to add the calculation to
        :param calculation: Details of new calculation 
        :returns: Response to create
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = self.request('/payslips/{}/calculations'.format(payslip_id),
                            method='POST',
                            json=calculation)
        return resp

    def delete_calculation(self, calculation_id: str) -> Dict[str, Any]:
        """Delete a specific calculation
        See: https://www.simplepay.co.za/api-docs/#delete-a-calculation

        :param calculation_id: The leave day to delete
        :returns: dictionary message on success
        '"""
        resp = self.request('/calculations/{}'.format(calculation_id),
                            method='DELETE')
        return resp.json()

    def get_service_periods(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of service periods for an employee
        See: https://www.simplepay.co.za/api-docs/#service-periods

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of service periods
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        return [sp['service_period'] for sp in self.request('/employees/{}/service_periods'.format(employee_id)).json()]
        
    async def get_service_periods_async(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get a list of service periods for an employee
        See: https://www.simplepay.co.za/api-docs/#service-periods

        :param employee_id: The employee id to return the calculation data for
        :returns: A list of service periods
        :raises NotFound: If a particular resource could not be found
        :raises SimplePayException: If there was an error in the response
        """
        resp = await self.request_async('/employees/{}/service_periods'.format(employee_id))
        return [sp['service_period'] for sp in resp]


class SimplePayException(Exception):
    """Raised when a resource could not be retrieved"""
    pass


class NotFound(SimplePayException):
    """Raised when a resource requested does not exist or cannot be accessed by the api key"""

