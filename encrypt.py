import json
import hashlib
import time

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

TASK_DESCRIPTION = (
    "Demo task: encrypt a harmless test payload and hold decryption until "
    "the approver explicitly authorizes it."
)

with open("keys/approver_public_key.pem", "rb") as f:
    approver_public_key = serialization.load_pem_public_key(f.read())

with open("payload/test_payload.txt", "rb") as f:
    plaintext = f.read()

data_key = Fernet.generate_key()
fernet = Fernet(data_key)
payload_enc = fernet.encrypt(plaintext)

with open("payload.enc", "wb") as f:
    f.write(payload_enc)

data_key_enc = approver_public_key.encrypt(
    data_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
with open("data_key.enc", "wb") as f:
    f.write(data_key_enc)

request = {
    "task": TASK_DESCRIPTION,
    "payload_sha256": hashlib.sha256(plaintext).hexdigest(),
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "status": "PENDING"
}
with open("approval_request.json", "w") as f:
    json.dump(request, f, indent=2)

print("Payload encrypted            -> payload.enc")
print("Data key wrapped (RSA-OAEP)  -> data_key.enc")
print("Approval request created     -> approval_request.json (status: PENDING)")
print()
print("Decryption is not possible until the approver runs approve.py")
print("and explicitly types APPROVE.")
