import json
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

with open("approval_request.json") as f:
    request = json.load(f)

if request["status"] == "APPROVED":
    print("This task has already been approved. Nothing to do.")
    raise SystemExit

print("=== APPROVAL REQUEST ===")
print(f"Task        : {request['task']}")
print(f"Payload hash: {request['payload_sha256']}")
print(f"Requested at: {request['created_at']}")
print("========================")

confirm = input('Type "APPROVE" to authorize decryption of this task, anything else to cancel: ')

if confirm.strip() != "APPROVE":
    print("Approval cancelled. Decryption remains locked.")
    raise SystemExit

with open("keys/approver_private_key.pem", "rb") as f:
    approver_private_key = serialization.load_pem_private_key(f.read(), password=None)

with open("data_key.enc", "rb") as f:
    data_key_enc = f.read()

data_key = approver_private_key.decrypt(
    data_key_enc,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

with open("released_data_key.bin", "wb") as f:
    f.write(data_key)

request["status"] = "APPROVED"
request["approved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
approval_bytes = json.dumps(request, sort_keys=True).encode()

signature = approver_private_key.sign(
    approval_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)
with open("approval_signature.bin", "wb") as f:
    f.write(signature)

with open("approval_request.json", "w") as f:
    json.dump(request, f, indent=2)

print()
print("APPROVED.")
print("Data key released      -> released_data_key.bin")
print("Approval record signed -> approval_signature.bin")
print("decrypt.py can now proceed.")
