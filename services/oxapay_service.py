import asyncio
import aiohttp
from config.settings import settings

class OxaPayService:
    BASE_URL = "https://api.oxapay.com/v1/payment"

    def __init__(self):
        self.api_key = settings.OXAPAY_API_KEY

    async def create_invoice(self, amount, order_id):
        url = f"{self.BASE_URL}/invoice"
        headers = {
            "merchant_api_key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "amount": amount,
            "currency": "USD",
            "to_currency": "USDT",
            "lifetime": 30,
            "fee_paid_by_payer": 1,
            "under_paid_coverage": 2.5,
            "auto_withdrawal": False,
            "mixed_payment": True,
            "description": order_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
               
                if response.status == 200:
                    d = data["data"]
                    track_id = d["track_id"]
                    payment_url = d["payment_url"]
                    expired_at = d["expired_at"]
                    invoice_date = d["date"]
                    parts =payment_url.split("/") 
                    merchant_id = parts[-2] 
                    return track_id, merchant_id, expired_at, invoice_date
                else:
                    raise Exception(f"❌ Create OxaPay invoice failed: {data}")
    async def create_invoice_renew(self, amount, order_id):
        url = f"{self.BASE_URL}/invoice"
        headers = {
            "merchant_api_key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "amount": amount,
            "currency": "USD",
            "to_currency": "USDT",
            "lifetime": 1440,
            "fee_paid_by_payer": 1,
            "under_paid_coverage": 2.5,
            "auto_withdrawal": False,
            "mixed_payment": True,
            "description": order_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
               
                if response.status == 200:
                    d = data["data"]
                    track_id = d["track_id"]
                    payment_url = d["payment_url"]
                    expired_at = d["expired_at"]
                    invoice_date = d["date"]
                    parts =payment_url.split("/") 
                    merchant_id = parts[-2] 
                    return track_id, merchant_id, expired_at, invoice_date
                else:
                    raise Exception(f"❌ Create OxaPay invoice failed: {data}")

    async def check_payment_status(self, track_id):
        url = f"{self.BASE_URL}/{track_id}"
        headers = {
            "merchant_api_key": self.api_key,
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                if response.status == 200:
                    status = data["data"]["status"]
                    if status == "paid":
                        return True
                    else:
                        return False
                else:
                    return False    

# if __name__ == "__main__":
#     async def main():
#         oxapay = OxaPayService()
#         try:
#             track_id, merchant_id, expired_at, invoice_date = await oxapay.create_invoice(10.0, "TEST_ORDER_123")
#             print(f"Invoice created: track_id={track_id}, merchant_id={merchant_id}, expired_at={expired_at}, invoice_date={invoice_date}")

#             is_paid = await oxapay.check_payment_status(track_id)
#             print(f"Payment status for track_id {track_id}: {'Paid' if is_paid else 'Not Paid'}")
#         except Exception as e:
#             print(str(e))

#     asyncio.run(main())