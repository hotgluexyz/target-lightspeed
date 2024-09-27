"""Lightspeed target sink class, which handles writing streams."""

import backoff
import requests
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.authenticators import BasicAuthenticator


from target_hotglue.client import HotglueSink
import base64

class LightspeedSink(HotglueSink):
    """Lightspeed target sink class."""

    variants = None
    products = None

    @property
    def base_url(self):
        language = self.config.get("language")
        return f'{self.config.get("base_url")}/{language}'
    
    @property
    def default_headers(self):
        headers = super().default_headers
        credentials = f"{self.config.get('api_key')}:{self.config.get('api_secret')}".encode('utf-8')
        encoded_credentials = base64.b64encode(credentials).decode('utf-8')
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Authorization"] = f"Basic {encoded_credentials}"
        return headers
    
    @backoff.on_exception(
    backoff.expo,
    (RetriableAPIError, requests.exceptions.ReadTimeout),
    max_tries=5,
    factor=2,
    )
    def _request(
        self, http_method, endpoint, params={}, request_data=None, headers={}
    ) -> requests.PreparedRequest:
        """Prepare a request object."""
        url = self.url(endpoint)
        headers.update(self.default_headers)
        params.update(self.params)

        response = requests.request(
            method=http_method,
            url=url,
            params=params,
            headers=headers,
            data=request_data
        )
        self.validate_response(response)
        return response
    
    def get_records(self, endpoint, fields, name, params={}) -> None:
        paginate = True
        page = 0
        records = []
        while paginate:
            page += 1
            req_params = {"page": page}
            if params:
                req_params.update(params)
            response = self.request_api("GET", endpoint, params=req_params)
            response_records = response.json().get(name, [])
            if response_records:
                records = records + response_records
            else:
                paginate = False
        return records
    
    def get_variants(self):
        if LightspeedSink.variants is None:
            LightspeedSink.variants = self.get_records("/variants.json", "id,stockLevel,title,sku,product", "variants")
        return LightspeedSink.variants
    
    def get_products(self):
        if LightspeedSink.products is None:
            LightspeedSink.products = self.get_records("/products.json", "id,title", "products")
        return LightspeedSink.products
    