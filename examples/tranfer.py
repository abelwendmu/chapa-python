from chapa import Chapa
import random
import string

def generate_tx_ref(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def example_transfer():
    chapa = Chapa('CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3')
    reference=generate_tx_ref()
    response = chapa.initiate_transfer(
        account_name="Israel Goytom",
        account_number="0900112233",
        amount="1",
        currency="ETB",
        bank_code=855, 
        reference=reference

    )
    print(response)

    if response['status'] == 'success':
        print("✅ Transfer queued:", response['data'],response)
    else:
        print("❌ Transfer failed:", response.get('message', 'Unknown error'))

def example_verify_transfer():
    chapa = Chapa("CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3")

    tx_ref = "4H58IBLC8J"  # Replace with your actual reference
    response = chapa.verify_transfer(tx_ref)

    if response["status"] == "success":
        print("✅ Transfer verification successful:")
        print("Recipient:", response["data"]["account_name"])
        print("Amount:", response["data"]["amount"])
        print("Bank:", response["data"]["bank_name"])
        print("Status:", response["data"]["status"])
    else:
        print("❌ Transfer verification failed:")
        print(response.get("message", "Unknown error"))

def test_get_balance():
    chapa = Chapa("CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3")

    # Get all balances
    response = chapa.get_balance()

    if response["status"] == "success":
        print("✅ Account Balances:")
        for b in response["data"]:
            print(f"{b['currency']}: Available = {b['available_balance']}, Ledger = {b['ledger_balance']}")
    else:
        print("❌ Failed to fetch balances:", response.get("message", "Unknown error"))

    # Optionally: Get only ETB balance
    etb_balance = chapa.get_balance("ETB")
    print("📌 ETB Only:", etb_balance)


def test_get_all_transfers():
    chapa = Chapa("CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3")

    # Optional filters, such as:
    filters = {
        # "status": "success",
        # "batch_id": "1234",
        # "limit": 10,
        # "page": 1
    }

    response = chapa.get_all_transfers(filters)
    if response["status"] == "success":
        print("✅ Transfers Retrieved:", len(response["data"]))
        for t in response["data"]:
            print("-", t["tx_ref"], "=>", t["status"])
    else:
        print("❌ Failed to retrieve transfers:", response.get("message", "Unknown error"))

def test_swap():
    chapa = Chapa("CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3")

    try:
        response = chapa.swap_currency(amount=100)

        if response["status"] == "success":
            print("✅ Swap Successful!")
            print("Exchanged:", response["data"]["amount"], response["data"]["from_currency"], "→",
                  response["data"]["exchanged_amount"], response["data"]["to_currency"])
            print("Rate:", response["data"]["rate"])
        else:
            print("❌ Swap Failed:", response.get("message", "Unknown error"))
    except Exception as e:
        print("❌ Error:", e)

def test_bulk_transfer():
    chapa = Chapa("CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3")

    transfers = [
        {
            "account_name": "Israel Goytom",
            "account_number": "0900112233",
            "amount": 50,
            "reference": generate_tx_ref(),
            "bank_code": 855
        },
        {
            "account_name": "Israel Goytom",
            "account_number": "0900112233",
            "amount": 75,
            "reference": generate_tx_ref(),
            "bank_code": 855
        }
    ]

    response = chapa.bulk_transfer(
        title="This Month Salary!",
        currency="ETB",
        bulk_data=transfers
    )
    print(response['message']['bulk_data'])
    if response["status"] == "success":
        print("✅ Bulk transfer queued successfully!")
        print("Batch ID:", response["data"]["id"])
    else:
        print("❌ Failed to queue bulk transfer:", response.get("message", "Unknown error"))





# test_bulk_transfer()
# test_swap()
# test_get_balance()
# example_verify_transfer()
# example_transfer()
# test_get_all_transfers()