import json
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

with open("approval_request.json") as f:
    request = json.load(f)

if request.get("status") != "APPROVED":
    print("DECRYPTION BLOCKED: this task has not been approved yet.")
    print("Run approve.py and explicitly confirm before decryption is possible.")
    raise SystemExit

if not os.path.exists("released_data_key.bin") or not os.path.exists("approval_signature.bin"):
    print("DECRYPTION BLOCKED: required approval artifacts are missing.")
    raise SystemExit

with open("keys/approver_public_key.pem", "rb") as f:
    approver_public_key = serialization.load_pem_public_key(f.read())
approval_bytes = json.dumps(request, sort_keys=True).encode()
with open("approval_signature.bin", "rb") as f:
    signature = f.read()
try:
    approver_public_key.verify(
        signature,
        approval_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
except Exception:
    print("DECRYPTION BLOCKED: approval signature is invalid or the record was tampered with.")
    raise SystemExit

print("Approval signature valid — authorization confirmed.")

with open("released_data_key.bin", "rb") as f:
    data_key = f.read()

with open("payload.enc", "rb") as f:
    payload_enc = f.read()

fernet = Fernet(data_key)
plaintext = fernet.decrypt(payload_enc)

with open("payload_decrypted.txt", "wb") as f:
    f.write(plaintext)

print("Payload decrypted -> payload_decrypted.txt")
print()
print("--- Decrypted content ---")
print(plaintext.decode())
