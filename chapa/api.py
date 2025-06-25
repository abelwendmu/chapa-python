"""
API SDK for Chapa Payment Gateway
"""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
import re
import json
from typing import Dict, Optional
import httpx





class Response:
    """Custom Response class for SMS handling."""

    def __init__(self, dict1):
        self.__dict__.update(dict1)


def convert_response(response: dict) -> Response:
    """
    Convert Response data to a Response object

    Args:
        response (dict): The response data to convert

    Returns:
        Response: The converted response
    """
    if not isinstance(response, dict):
        return response

    return json.loads(json.dumps(response), object_hook=Response)


class Chapa:
    """
    Simple SDK for Chapa Payment gateway
    """

    def __init__(
        self,
        secret,
        base_ur="https://api.chapa.co",
        api_version="v1",
        response_format="json",
    ):
        self._key = secret
        self.base_url = base_ur
        self.api_version = api_version
        if response_format and response_format in ["json", "obj"]:
            self.response_format = response_format
        else:
            raise ValueError("response_format must be 'json' or 'obj'")

        self.headers = {"Authorization": f"Bearer {self._key}"}
        self.client = httpx.Client()

    def send_request(self, url, method, data=None, params=None, headers=None):
        """
        Request sender to the api

        Args:
            url (str): url for the request to be sent.
            method (str): the method for the request.
            data (dict, optional): request body. Defaults to None.

        Returns:
            response: response of the server.
        """
        if params and not isinstance(params, dict):
            raise ValueError("params must be a dict")

        if data and not isinstance(data, dict):
            raise ValueError("data must be a dict")

        if headers and isinstance(data, dict):
            headers.update(self.headers)
        elif headers and not isinstance(data, dict):
            raise ValueError("headers must be a dict")
        else:
            headers = self.headers

        func = getattr(self.client, method)
        if method.lower() == "get":
            response = func(url, params=params or data, headers=headers)
        else:
            response = func(url, data=data, headers=headers)
        return getattr(response, "json", lambda: response.text)()

    def _construct_request(self, *args, **kwargs):
        """Construct the request to send to the API"""

        res = self.send_request(*args, **kwargs)
        if self.response_format == "obj" and isinstance(res, dict):
            return convert_response(res)

        return res

    def initialize(
        self,
        email: str,
        amount: int,
        first_name: str,
        last_name: str,
        tx_ref: str,
        currency="ETB",
        phone_number=None,
        callback_url=None,
        return_url=None,
        customization=None,
        headers=None,
        **kwargs,
    ) -> dict | Response:
        """
        Initialize the Transaction

        Args:
            email (str): customer email
            amount (int): amount to be paid
            first_name (str): first name of the customer
            last_name (str): last name of the customer
            tx_ref (str): your transaction id
            phone_number (str, optional): phone number of the customer.
                                          Defaults to None.
            currency (str, optional): currency the transaction. Defaults to 'ETB'.
            callback_url (str, optional): function that runs when payment is successful.
                                          Defaults to None.
            return_url (str, optional): web address to redirect the user after payment is
                                        successful. Defaults to None.
            customization (dict, optional): customization, currently 'title' and 'description'
                                            are available. Defaults to None.
            headers(dict, optional): header to attach on the request. Default to None

        Return:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "currency": currency,
        }

        if kwargs:
            data.update(kwargs)

        if not isinstance(amount, int):
            if str(amount).replace(".", "", 1).isdigit() and float(amount) > 0:
                pass
            else:
                raise ValueError("invalid amount")
        elif isinstance(amount, int):
            if amount < 0:
                raise ValueError("invalid amount")

        data["amount"] = amount

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("invalid email")

        data["email"] = email

        if phone_number:
            data["phone_number"] = phone_number

        if callback_url:
            data["callback_url"] = callback_url

        if return_url:
            data["return_url"] = return_url

        if customization:
            if "title" in customization:
                data["customization[title]"] = customization["title"]
            if "description" in customization:
                data["customization[description]"] = customization["description"]
            if "logo" in customization:
                data["customization[logo]"] = customization["logo"]

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transaction/initialize",
            method="post",
            data=data,
            headers=headers,
        )
        return response

    def verify(self, transaction: str, headers=None) -> dict | Response:
        """Verify the transaction

        Args:
            transaction (str): transaction id

        Response:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transaction/verify/{transaction}",
            method="get",
            headers=headers,
        )
        return response

    def create_subaccount(
        self,
        business_name: str,
        account_name: str,
        bank_code: str,
        account_number: str,
        split_value: str,
        split_type: str,
        headers=None,
        **kwargs,
    ) -> dict | Response:
        """
        Create a subaccount for split payment

        Args:
            business_name (str): business name
            account_name (str): account name
            bank_code (str): bank code
            account_number (str): account number
            split_value (str): split value
            split_type (str): split type
            headers(dict, optional): header to attach on the request. Default to None
            **kwargs: additional data to be sent to the server

        Return:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """

        data = {
            "business_name": business_name,
            "account_name": account_name,
            "bank_code": bank_code,
            "account_number": account_number,
            "split_value": split_value,
            "split_type": split_type,
        }

        if kwargs:
            data.update(kwargs)

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/subaccount",
            method="post",
            data=data,
            headers=headers,
        )
        return response

    def initialize_split_payment(
        self,
        amount: int,
        currency: str,
        email: str,
        first_name: str,
        last_name: str,
        tx_ref: str,
        callback_url: str,
        return_url: str,
        subaccount_id: str,
        headers=None,
        **kwargs,
    ) -> dict | Response:
        """
        Initialize split payment transaction

        Args:
            email (str): customer email
            amount (int): amount to be paid
            first_name (str): first name of the customer
            last_name (str): last name of the customer
            tx_ref (str): your transaction id
            currency (str, optional): currency the transaction. Defaults to 'ETB'.
            callback_url (str, optional): url for the customer to redirect after payment.
                                          Defaults to None.
            return_url (str, optional): url for the customer to redirect after payment.
                                          Defaults to None.
            subaccount_id (str, optional): subaccount id to split payment.
                                          Defaults to None.
            headers(dict, optional): header to attach on the request. Default to None
            **kwargs: additional data to be sent to the server

        Return:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "currency": currency,
            "callback_url": callback_url,
            "return_url": return_url,
            "subaccount_id": subaccount_id,
        }

        if kwargs:
            data.update(kwargs)

        if not isinstance(amount, int):
            if str(amount).replace(".", "", 1).isdigit() and float(amount) > 0:
                pass
            else:
                raise ValueError("invalid amount")
        elif isinstance(amount, int):
            if amount < 0:
                raise ValueError("invalid amount")

        data["amount"] = amount

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("invalid email")

        data["email"] = email

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transaction/initialize",
            method="post",
            data=data,
            headers=headers,
        )
        return response
    
    #transfer
    def initiate_transfer(
        self,
        account_name: str,
        account_number: str,
        amount: str,
        currency: str,
        bank_code: int,
        reference: str = None,
    ):
        """
        Initiates a transfer request to a bank account.

        Args:
            account_name (str): Recipient's full name.
            account_number (str): Recipient's bank account number.
            amount (str): Amount to transfer.
            currency (str): Currency (e.g., "ETB").
            bank_code (int): Bank code of the recipient's bank.
            reference (str, optional): A unique reference for the transfer.

        Returns:
            dict or Response: Parsed response from Chapa.
        """

        payload = {
            "account_name": account_name,
            "account_number": account_number,
            "amount": amount,
            "currency": currency,
            "bank_code": bank_code,
        }

        if reference:
            payload["reference"] = reference

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transfers",
            method="post",
            data=payload,
            headers=headers,
        )
        return response
    def get_banks(self, headers=None) -> dict | Response:
        """Get the list of all banks

        Response:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/banks",
            method="get",
            headers=headers,
        )
        return response


    def verify_transfer(self, reference: str) -> dict | Response:
        """Verify the status of a transfer

        This section describes how to verify the status of a transfer with Chapa

        Args:
            reference (str): This a merchant’s uniques reference for the transfer, it can be used to query for the status of the transfer

        Returns:
            dict: response from the server
                - message: str
                - status: str
                - data: str | None
            response(Response): response object of the response data return from the Chapa server.
        """
        
        url = f"{self.base_url}/{self.api_version}/transfers/verify/{reference}"
        response = self._construct_request(
            url=url,
            method="get",
        )
        return response
    

    
    def bulk_transfer(self, title: str, currency: str, bulk_data: list):
        """
        Initiates a bulk transfer to multiple recipients.

        Args:
            title (str): A descriptive title for the batch (e.g. "April Payroll").
            currency (str): Currency (e.g. "ETB").
            bulk_data (list): A list of transfer dicts, each containing:
                account_name, account_number, amount, reference, bank_code

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        if not isinstance(bulk_data, list) or len(bulk_data) == 0:
            raise ValueError("bulk_data must be a non-empty list of transfer items")

        if len(bulk_data) > 100:
            raise ValueError("bulk_data must not contain more than 100 items")

        url = f"{self.base_url}/{self.api_version}/bulk-transfers"

        payload = {
            "title": title,
            "currency": currency,
            "bulk_data": bulk_data
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=url,
            method="post",
            data=payload,
            headers=headers,
        )
        return response
        


    def get_bulk_transfer_status(self, batch_id: str):
        """
        Retrieves the status of a bulk transfer using its batch_id.

        Args:
            batch_id (str): ID returned from the initial bulk transfer request.

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        url = f"{self.base_url}/{self.api_version}/transfers"
        headers = {
            "Authorization": f"Bearer {self._key}"
        }

        params = {
            "batch_id": batch_id
        }

        response = self.client.get(url, headers=headers, params=params)
        parsed = getattr(response, "json", lambda: response.text)()

        if self.response_format == "obj" and isinstance(parsed, dict):
            return convert_response(parsed)

        return parsed
    def get_all_transfers(self, filters: dict = None):
        """
        Retrieves all transfers for your account.
        
        Args:
            filters (dict, optional): Optional query parameters such as:
                - status
                - batch_id
                - date ranges (start_date, end_date)
                - limit, page, etc.

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        url = f"{self.base_url}/{self.api_version}/transfers"
        headers = dict(Authorization=f"Bearer {self._key}")
        response = self._construct_request(
            url=url,
            method="get",
            params=filters or {}
        )
        return response
        


    def get_balance(self, currency_code: str = None):
        """
        Retrieves the current balance from your Chapa account.

        Args:
            currency_code (str, optional): If provided, filters balance for specific currency
                (e.g., "ETB", "USD"). If None, returns all balances.

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        endpoint = f"{self.base_url}/{self.api_version}/balances"
        if currency_code:
            endpoint += f"/{currency_code.lower()}"

        headers = {
            "Authorization": f"Bearer {self._key}"
        }

        response = self.client.get(endpoint, headers=headers)
        parsed = getattr(response, "json", lambda: response.text)()

        if self.response_format == "obj" and isinstance(parsed, dict):
            return convert_response(parsed)

        return parsed
    def swap_currency(self, amount: float, from_currency: str = "USD", to_currency: str = "ETB"):
        """
        Swaps USD to ETB using Chapa's Swap API.

        Args:
            amount (float): The amount in USD to convert. Min: 1, Max: 10,000.
            from_currency (str): Source currency. Only 'USD' is currently supported.
            to_currency (str): Target currency. Only 'ETB' is currently supported.

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        if amount < 1 or amount > 10000:
            raise ValueError("Amount must be between 1 and 10,000 USD")

        if from_currency.upper() != "USD" or to_currency.upper() != "ETB":
            raise ValueError("Currently only USD to ETB swap is supported")

        url = f"{self.base_url}/{self.api_version}/swap"

        payload = {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper()
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json"
        }

        response = self.client.post(url, json=payload, headers=headers)
        parsed = getattr(response, "json", lambda: response.text)()

        if self.response_format == "obj" and isinstance(parsed, dict):
            return convert_response(parsed)

        return parsed



  # - Direct Charge
    #   - Initiate Payments
    #   - Authorize Payments
    #   - Encryption


    def initiate_payment(self, *, payment_type: str, amount: str, currency: str, tx_ref: str, mobile: str):
        """
        Initiates a direct charge to the customer using the specified payment method.

        Args:
            payment_type (str): The payment method. Allowed values: telebirr, mpesa, cbebirr, ebirr, enat_bank.
            amount (str): Amount to charge the customer.
            currency (str): Currency to use. Only 'ETB' is supported.
            tx_ref (str): Unique transaction reference.
            mobile (str): Customer's phone number.

        Returns:
            dict or Response: API response (parsed JSON or Response object depending on response_format).
        """
        if payment_type not in ["telebirr", "mpesa", "cbebirr", "ebirr", "enat_bank"]:
            raise ValueError("Invalid payment type provided.")


        
        data = {
        "amount": amount,
        "currency": currency,
        "tx_ref": tx_ref,
        "mobile": mobile
             }
    
        headers = {
            "Authorization": f"Bearer {self._key}",
        }

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/charges?type={payment_type}",
            method="post",
            data=data,
            headers=headers,
        )
       
        return response
    def authorize_payment(self, *, payment_type: str, reference: str, encrypted_client_payload: str):
        """
        Authorize a direct charge transaction after initialization (e.g., OTP or USSD confirmation).

        Args:
            payment_type (str): Payment method (e.g., amole, telebirr, mpesa, cbebirr, ebirr, etc.).
            reference (str): Transaction reference (tx_ref).
            encrypted_client_payload (str): 3DES encrypted client payload string.

        Returns:
            dict or Response: Parsed JSON or Response object, depending on the response_format.
        """
        if not all([payment_type, reference, encrypted_client_payload]):
            raise ValueError("Missing one or more required parameters: payment_type, reference, client payload")



        data = {
            "reference": reference,
            "client": encrypted_client_payload
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/validate?type={payment_type}",
            method="post",
            data=data,
            headers=headers,
        )

        return response


    # Refund
    def refund(self, tx_ref: str, amount: Optional[str] = None, reason: Optional[str] = None, reference: Optional[str] = None, meta: Optional[Dict] = None, headers: Optional[Dict] = None) -> dict | Response:
        """
        Initiate a refund for a specific transaction.

        Args:
            tx_ref (str): The transaction reference provided by Chapa during initialization.
            amount (str, optional): Amount to refund. If not provided, the full transaction amount will be refunded.
            reason (str, optional): Reason for the refund.
            reference (str, optional): A unique identifier for this refund request.
            meta (dict, optional): Additional metadata.
            headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: response from the server
            response(Response): response object of the response data returned from the Chapa server.
        """
        data = {}
        if amount:
            data['amount'] = amount
        if reason:
            data['reason'] = reason
        if reference:
            data['reference'] = reference
        if meta and isinstance(meta, dict):
            for key, value in meta.items():
                data[f"meta[{key}]"] = value

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/refund/{tx_ref}",
            method="post",
            data=data,
            headers=headers,
        )
        return response

class AsyncChapa:
    def __init__(
        self,
        secret: str,
        base_ur: str = "https://api.chapa.co",
        api_version: str = "v1",
        response_format: str = "json",
    ) -> None:
        self._key = secret
        self.base_url = base_ur
        self.api_version = api_version
        if response_format and response_format in ["json", "obj"]:
            self.response_format = response_format
        else:
            raise ValueError("response_format must be 'json' or 'obj'")

        self.headers = {"Authorization": f"Bearer {self._key}"}
        self.client = httpx.AsyncClient()

    async def send_request(
        self,
        url: str,
        method: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """
        Request sender to the api

        Args:
            url (str): url for the request to be sent.
            method (str): the method for the request.
            data (dict, optional): request body. Defaults to None.

        Returns:
            response: response of the server.
        """
        if params and not isinstance(params, dict):
            raise ValueError("params must be a dict")

        if data and not isinstance(data, dict):
            raise ValueError("data must be a dict")

        if headers and isinstance(data, dict):
            headers.update(self.headers)
        elif headers and not isinstance(data, dict):
            raise ValueError("headers must be a dict")
        
        else:
            headers = self.headers

        async with self.client as client:
            func = getattr(client, method)
            response = await func(url, data=data, headers=headers)
            return getattr(response, "json", lambda: response.text)()

    async def _construct_request(self, *args, **kwargs):
        """Construct the request to send to the API"""

        res = await self.send_request(*args, **kwargs)
        if self.response_format == "obj" and isinstance(res, dict):
            return convert_response(res)

        return res

    async def initialize(
        self,
        *,
        email: Optional[str] = None,
        amount: float,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        tx_ref: str,
        currency: str,
        callback_url: Optional[str] = None,
        return_url: Optional[str] = None,
        customization: Optional[Dict] = None,
        subaccount_id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the Transaction and Get a payment link

        Once all the information needed to proceed with the transaction is retrieved, the action taken further would be to associate the following information into the javascript function(chosen language) which will innately display the checkout.


        Args:
            amount (float): A customer’s email. address
            tx_ref (str): A unique reference given to each transaction.
            currency (str): The currency in which all the charges are made. Currency allowed is ETB and USD.
            email (Optional[str], optional): A customer’s email. address. Defaults to None.
            first_name (Optional[str], optional): A customer’s first name. Defaults to None.
            last_name (Optional[str], optional): A customer’s last name. Defaults to None.
            phone_number (Optional[str], optional): The customer’s phone number. Defaults to None.
            callback_url (Optional[str], optional): Function that runs when payment is successful. This should ideally be a script that uses the verify endpoint on the Chapa API to check the status of the transaction. Defaults to None.
            return_url (Optional[str], optional): Web address to redirect the user after payment is successful. Defaults to None.
            customization (Optional[Dict], optional): The customizations field (optional) allows you to customize the look and feel of the payment modal. You can set a logo, the store name to be displayed (title), and a description for the payment. Defaults to None.
            subaccount_id (Optional[str], optional): The subaccount id to split payment. Defaults to None.
            **kwargs: Additional data to be sent to the server.

        Returns:
            dict: response from the server
                - message: str
                - status: str
                - data: dict
                    - checkout_url: str
            response(Response): response object of the response data return from the Chapa server.

        Raises:
            ValueError: If the parameters are invalid.
        """
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "currency": currency,
        }

        if subaccount_id:
            data["subaccount"] = {"id": subaccount_id}

        if kwargs:
            data.update(kwargs)

        if not isinstance(amount, int):
            if str(amount).replace(".", "", 1).isdigit() and float(amount) > 0:
                pass
            else:
                raise ValueError("invalid amount")
        elif isinstance(amount, int):
            if amount < 0:
                raise ValueError("invalid amount")

        data["amount"] = amount

        regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        if not regex.match(email):
            raise ValueError("invalid email")

        data["email"] = email

        if phone_number:
            data["phone_number"] = phone_number

        if callback_url:
            data["callback_url"] = callback_url

        if return_url:
            data["return_url"] = return_url

        if customization:
            if "title" in customization:
                data["customization[title]"] = customization["title"]
            if "description" in customization:
                data["customization[description]"] = customization["description"]
            if "logo" in customization:
                data["customization[logo]"] = customization["logo"]

        response = await self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transaction/initialize",
            method="post",
            data=data,
        )
        return response

    async def verify(self, tx_ref: str, headers: Optional[Dict] = None):
        """Verify the transaction

        Args:
            tx_ref (str): transaction id

        Returns:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """
        response = await self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transaction/verify/{tx_ref}",
            method="get",
            headers=headers,
        )
        return response

    async def create_subaccount(
        self,
        bank_code: str,
        account_number: str,
        business_name: str,
        account_name: str,
        split_type: str,
        split_value: str,
        headers: Optional[Dict] = None,
        **kwargs,
    ):
        """
        Create a subaccount for split payment.

        **Note:** that sub-accounts are working with ETB currency as a default settlement. This means if we get subaccount in your payload regardless of the currency we will convert it to ETB and do the settlement.

        Args:
            bank_code (str): The bank account details for this subaccount. The bank_code is the bank id (you can get this from the get banks endpoint).
            account_number (str): The account_number is the bank account number.
            business_name (str): The vendor/merchant detail the subaccount for.
            account_name (str): The vendor/merchant account’s name matches from the bank account.
            split_type (str): The type of split you want to use with this subaccount.
                - Use flat if you want to get a flat fee from each transaction, while the subaccount gets the rest.
                - Use percentage if you want to get a percentage of each transaction.
            split_value (str): The amount you want to get as commission on each transaction. This goes with the split_type.
                Example:
                    - to collect 3% from each transaction, split_type will be percentage and split_value will be 0.03.
                    - to collect 25 Birr from each transaction, split_type will be flat and split_value will be 25.
            headers(dict, optional): header to attach on the request. Default to None
            **kwargs: additional data to be sent to the server

        Return:
            dict: response from the server
                - message: str
                - status: str
                - data: dict
                    - subaccounts[id]": str
            response(Response): response object of the response data return from the Chapa server.
        """

        data = {
            "business_name": business_name,
            "account_name": account_name,
            "bank_code": bank_code,
            "account_number": account_number,
            "split_value": split_value,
            "split_type": split_type,
        }

        if kwargs:
            data.update(kwargs)

        response = await self._construct_request(
            url=f"{self.base_url}/{self.api_version}/subaccount",
            method="post",
            data=data,
            headers=headers,
        )
        return response

    async def get_banks(self, headers: Optional[Dict] = None):
        """Get the list of all banks

        Returns:
            dict: response from the server
            response(Response): response object of the response data return from the Chapa server.
        """
        response = await self._construct_request(
            url=f"{self.base_url}/{self.api_version}/banks",
            method="get",
            headers=headers,
        )
        return response

    #transfer
    async def initiate_transfer(
        self,
        account_name: str,
        account_number: str,
        amount: str,
        currency: str,
        bank_code: int,
        reference: str = None,
    ):
        """
        Initiates a transfer request to a bank account.

        Args:
            account_name (str): Recipient's full name.
            account_number (str): Recipient's bank account number.
            amount (str): Amount to transfer.
            currency (str): Currency (e.g., "ETB").
            bank_code (int): Bank code of the recipient's bank.
            reference (str, optional): A unique reference for the transfer.

        Returns:
            dict or Response: Parsed response from Chapa.
        """

        payload = {
            "account_name": account_name,
            "account_number": account_number,
            "amount": amount,
            "currency": currency,
            "bank_code": bank_code,
        }

        if reference:
            payload["reference"] = reference

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/transfers",
            method="post",
            data=payload,
            headers=headers,
        )
        return response



    async def verify_transfer(self, reference: str) -> dict | Response:
        """Verify the status of a transfer

        This section describes how to verify the status of a transfer with Chapa

        Args:
            reference (str): This a merchant’s uniques reference for the transfer, it can be used to query for the status of the transfer

        Returns:
            dict: response from the server
                - message: str
                - status: str
                - data: str | None
            response(Response): response object of the response data return from the Chapa server.
        """
        
        url = f"{self.base_url}/{self.api_version}/transfers/verify/{reference}"
        response = self._construct_request(
            url=url,
            method="get",
        )
        return response
    

    
    async def bulk_transfer(self, title: str, currency: str, bulk_data: list):
        """
        Initiates a bulk transfer to multiple recipients.

        Args:
            title (str): A descriptive title for the batch (e.g. "April Payroll").
            currency (str): Currency (e.g. "ETB").
            bulk_data (list): A list of transfer dicts, each containing:
                account_name, account_number, amount, reference, bank_code

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        if not isinstance(bulk_data, list) or len(bulk_data) == 0:
            raise ValueError("bulk_data must be a non-empty list of transfer items")

        if len(bulk_data) > 100:
            raise ValueError("bulk_data must not contain more than 100 items")

        url = f"{self.base_url}/{self.api_version}/bulk-transfers"

        payload = {
            "title": title,
            "currency": currency,
            "bulk_data": bulk_data
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=url,
            method="post",
            data=payload,
            headers=headers,
        )
        return response
        
    async def swap_currency(self, amount: float, from_currency: str = "USD", to_currency: str = "ETB"):
        """
        Swaps USD to ETB using Chapa's Swap API.

        Args:
            amount (float): The amount in USD to convert. Min: 1, Max: 10,000.
            from_currency (str): Source currency. Only 'USD' is currently supported.
            to_currency (str): Target currency. Only 'ETB' is currently supported.

        Returns:
            dict or Response: Parsed response from Chapa.
        """
        if amount < 1 or amount > 10000:
            raise ValueError("Amount must be between 1 and 10,000 USD")

        if from_currency.upper() != "USD" or to_currency.upper() != "ETB":
            raise ValueError("Currently only USD to ETB swap is supported")

        url = f"{self.base_url}/{self.api_version}/swap"

        payload = {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper()
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json"
        }

        response = self.client.post(url, json=payload, headers=headers)
        parsed = getattr(response, "json", lambda: response.text)()

        if self.response_format == "obj" and isinstance(parsed, dict):
            return convert_response(parsed)

        return parsed



  # - Direct Charge
    #   - Initiate Payments
    #   - Authorize Payments
    #   - Encryption


    async def initiate_payment(self, *, payment_type: str, amount: str, currency: str, tx_ref: str, mobile: str):
        """
        Initiates a direct charge to the customer using the specified payment method.

        Args:
            payment_type (str): The payment method. Allowed values: telebirr, mpesa, cbebirr, ebirr, enat_bank.
            amount (str): Amount to charge the customer.
            currency (str): Currency to use. Only 'ETB' is supported.
            tx_ref (str): Unique transaction reference.
            mobile (str): Customer's phone number.

        Returns:
            dict or Response: API response (parsed JSON or Response object depending on response_format).
        """
        if payment_type not in ["telebirr", "mpesa", "cbebirr", "ebirr", "enat_bank"]:
            raise ValueError("Invalid payment type provided.")


        
        data = {
        "amount": amount,
        "currency": currency,
        "tx_ref": tx_ref,
        "mobile": mobile
             }
    
        headers = {
            "Authorization": f"Bearer {self._key}",
        }

        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/charges?type={payment_type}",
            method="post",
            data=data,
            headers=headers,
        )
       
        return response
    async def authorize_payment(self, *, payment_type: str, reference: str, encrypted_client_payload: str):
        """
        Authorize a direct charge transaction after initialization (e.g., OTP or USSD confirmation).

        Args:
            payment_type (str): Payment method (e.g., amole, telebirr, mpesa, cbebirr, ebirr, etc.).
            reference (str): Transaction reference (tx_ref).
            encrypted_client_payload (str): 3DES encrypted client payload string.

        Returns:
            dict or Response: Parsed JSON or Response object, depending on the response_format.
        """
        if not all([payment_type, reference, encrypted_client_payload]):
            raise ValueError("Missing one or more required parameters: payment_type, reference, client payload")



        data = {
            "reference": reference,
            "client": encrypted_client_payload
        }

        headers = {
            "Authorization": f"Bearer {self._key}",
        }
        response = self._construct_request(
            url=f"{self.base_url}/{self.api_version}/validate?type={payment_type}",
            method="post",
            data=data,
            headers=headers,
        )

        return response



    
    # Refund
    async def refund(self, tx_ref: str, amount: Optional[str] = None, reason: Optional[str] = None, reference: Optional[str] = None, meta: Optional[Dict] = None, headers: Optional[Dict] = None) -> dict | Response:
        """
        Initiate an asynchronous refund for a specific transaction.

        Args:
            tx_ref (str): The transaction reference provided by Chapa during initialization.
            amount (str, optional): Amount to refund. If not provided, the full transaction amount will be refunded.
            reason (str, optional): Reason for the refund.
            reference (str, optional): A unique identifier for this refund request.
            meta (dict, optional): Additional metadata.
            headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: response from the server
            response(Response): response object of the response data returned from the Chapa server.
        """
        data = {}
        if amount:
            data['amount'] = amount
        if reason:
            data['reason'] = reason
        if reference:
            data['reference'] = reference
        if meta and isinstance(meta, dict):
            for key, value in meta.items():
                data[f"meta[{key}]"] = value

        response = await self._construct_request(
            url=f"{self.base_url}/{self.api_version}/refund/{tx_ref}",
            method="post",
            data=data,
            headers=headers,
        )
        return response


def get_testing_cards(self):
    """Get the list of all testing cards

    Returns:
        List[dict]: all testing cards
    """
    testing_cards = [
        {
            "Brand": "Visa",
            "Card Number": "4200 0000 0000 0000",
            "CVV": "123",
            "Expiry": "12/34",
        },
        {
            "Brand": "Amex",
            "Card Number": "3700 0000 0000 0000",
            "CVV": "1234",
            "Expiry": "12/34",
        },
        {
            "Brand": "Mastercard",
            "Card Number": "5400 0000 0000 0000",
            "CVV": "123",
            "Expiry": "12/34",
        },
        {
            "Brand": "Union Pay",
            "Card Number": "6200 0000 0000 0000",
            "CVV": "123",
            "Expiry": "12/34",
        },
        {
            "Brand": "Diners",
            "Card Number": "3800 0000 0000 0000",
            "CVV": "123",
            "Expiry": "12/34",
        },
    ]

    return testing_cards


def get_testing_mobile(self):
    """
    Get the list of all testing mobile numbers

    Returns:
        List[dict]: all testing mobile numbers
    """
    testing_mobile = [
        {"Bank": "Awash Bank", "Phone": "0900123456", "OTP": "12345"},
        {"Bank": "Awash Bank", "Phone": "0900112233", "OTP": "12345"},
        {"Bank": "Awash Bank", "Phone": "0900881111", "OTP": "12345"},
        {"Bank": "Amole", "Phone": "0900123456", "OTP": "12345"},
        {"Bank": "Amole", "Phone": "0900112233", "OTP": "12345"},
        {"Bank": "Amole", "Phone": "0900881111", "OTP": "12345"},
        {"Bank": "telebirr", "Phone": "0900123456", "OTP": "12345"},
        {"Bank": "telebirr", "Phone": "0900112233", "OTP": "12345"},
        {"Bank": "telebirr", "Phone": "0900881111", "OTP": "12345"},
        {"Bank": "CBEBirr", "Phone": "0900123456", "OTP": "12345"},
        {"Bank": "CBEBirr", "Phone": "0900112233", "OTP": "12345"},
        {"Bank": "CBEBirr", "Phone": "0900881111", "OTP": "12345"},
        {"Bank": "COOPPay-ebirr", "Phone": "0900123456", "OTP": "12345"},
        {"Bank": "COOPPay-ebirr", "Phone": "0900112233", "OTP": "12345"},
        {"Bank": "COOPPay-ebirr", "Phone": "0900881111", "OTP": "12345"},
    ]
    return testing_mobile
