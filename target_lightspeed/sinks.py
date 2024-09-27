"""Lightspeed target sink class, which handles writing streams."""

from __future__ import annotations


from target_lightspeed.client import LightspeedSink

class UpdateInventorySink(LightspeedSink):
    """Lightspeed target sink class."""

    endpoint = "/variants" # stockLevel is only available in variants not in products
    name = "UpdateInventory"


    def preprocess_record(self, record: dict, context: dict) -> dict:
        # fetch all variants

        variants = self.get_variants()

        # build payload
        payload = {}
        product_id = record.get("id")
        variant_id = record.get("variant_id")
        sku = record.get("sku")
        name = record.get("product_name", record.get("name"))
        variant = {}

        if product_id:
            # check id as a variant
            variant = next((variant for variant in variants if str(variant["id"]) == str(product_id)), None)
            # check id as a product
            if not variant:
                product_variants = [variant for variant in variants if str(variant["product"]["resource"]["id"]) == str(product_id)]
                if len(product_variants) == 1:
                    variant = product_variants[0]
                elif len(product_variants) > 1:
                    return {"error": f"Stock is only updatable for variants. Product id {product_id} has many variants, please send the variant sku or id to update the stock"}

        if variant_id and not variant:
            variant = next((variant for variant in variants if str(variant["id"]) == str(variant_id)), None)
        if sku and not variant:
            # Only variants have sku, find variant using sku. 
            variant = next((variant for variant in variants if variant.get("sku") == sku), None)
        if name and not variant:
            # check variant by name
            variant = next((variant for variant in variants if variant.get("title") == name), None)
            # check product by name
            if not variant:
                products = self.get_products()
                product = next((product for product in products if product.get("title") == name), None)
                if product:
                    prod_id = product["id"]
                    product_variants = [variant for variant in variants if str(variant["product"]["resource"]["id"]) == str(prod_id)]
                    if len(product_variants) == 1:
                        variant = product_variants[0]
                    elif len(product_variants) > 1:
                        return {"error": f"Stock is only updatable for variants. Product '{name}' with id {prod_id} has many variants, please send the variant sku or id to update the stock"}
        
        if not variant: 
            return {"error": f"Stock is only updatable for variants. Product id {product_id} has many variants, please send the variant sku or id to update the stock"}
                
        # calculate stockLevel
        id = variant.get("id")
        current_stock = variant.get("stockLevel", 0)
        operation = record["operation"]
        if  operation == "subtract":
            new_stock = current_stock - int(record["quantity"])
        elif operation == "set":
            new_stock = int(record["quantity"])
        elif operation == "add":
            new_stock = current_stock + int(record["quantity"])

        self.logger.info(f"variant with sku '{variant.get('sku')}' and id {variant['id']} current stock: {current_stock}, executing operation '{operation}' with quantity {record['quantity']}")
        
        # build payload
        payload = {
            "id": id,
            "variant[stockLevel]": new_stock
        }
        return payload 


    def upsert_record(self, record: dict, context: dict) -> None:
        """Process the record."""
        state_updates = dict()
        if record:
            if record.get("error"):
                raise Exception(record["error"])
            
            endpoint = f"{self.endpoint}/{record.pop('id')}.json"
            self.logger.info(f"Making request to endpoint='{self.endpoint}' with method: 'PUT' and payload= {record}")
            response = self.request_api(
                "PUT", endpoint=endpoint, request_data=record
            )
            res_json = response.json().get("variant")
            variant_id = res_json.get("id")
            new_stock_level = res_json.get('stockLevel')
            self.logger.info(f"Variant with id {variant_id} updated.  New stock {new_stock_level}")
            # add new stock to the variants list, in case there's 2 records for the same variant
            variant = [variant for variant in LightspeedSink.variants if variant["id"] == variant_id]
            # variant[0]["stockLevel"] = new_stock_level
            return variant_id, True, state_updates