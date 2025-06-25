from chapa import Chapa
import random
import string
from Crypto.Cipher import DES3
import base64

def pad(text: str):
    pad_len = 8 - (len(text) % 8)
    return text + chr(pad_len) * pad_len

def encrypt_3des(payload: str, secret_key: str) -> str:
    """Encrypt the client payload using 3DES ECB mode."""
    key = secret_key[:24]  # 24 bytes for 3DES
    cipher = DES3.new(key.encode(), DES3.MODE_ECB)
    padded_payload = pad(payload)
    encrypted = cipher.encrypt(padded_payload.encode())
    return base64.b64encode(encrypted).decode()


def generate_tx_ref(length=12):
    """Generate a random transaction reference."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def direct_charge():
    # Create Chapa instance with test secret key
    chapa = Chapa('CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3')

    tx_ref = generate_tx_ref()

    try:
        response = chapa.initiate_payment(
            payment_type='telebirr',
            amount='10',
            currency='ETB',
            tx_ref=tx_ref,
            mobile='0900123456'  # Replace with a valid test number if needed
        )
        print("Initiating direct charge with transaction reference:", response)

        if response['status'] == 'success':
            print("✅ Direct charge initiated successfully:")
            print("Message:", response['message'])
            print("USSD Auth Type:", response['data']['auth_type'])
    except Exception as e:
        print("❌ Error occurred while initiating direct charge:")
        print("Error:", str(e))

def authorize_payment_example():
    chapa = Chapa('CHASECK_TEST-8IYBy3gEpNPFrCbKLZmpSG9KX6QX5sO3', response_format='json')

    # Example raw payload to encrypt, e.g., {"otp": "1234"} as a string
    raw_payload = '{"otp": "1234"}'
    secret_encryption_key = 'WynhF8jzGPH11UuFV8MgYImf'  # Must be 24 bytes

    encrypted_client = encrypt_3des(raw_payload, secret_encryption_key)

    response = chapa.authorize_payment(
        payment_type='amole',
        reference='CHwOSObTZXJXf',
        encrypted_client_payload=encrypted_client
    )

    print(response)


# direct_charge()
# authorize_payment_example()

