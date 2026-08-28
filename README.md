# Encryption + Approval-Based Decryption (Demo)

A safe, harmless demonstration of **envelope encryption gated by explicit
human approval**. No real or malicious payload is used — just a plain text
test file.

## Concept

1. A payload is encrypted with a random one-time AES key (`data_key`).
2. `data_key` itself is **wrapped (encrypted) with the approver's RSA public
   key** (RSA-OAEP). This means the only way to ever recover `data_key` is
   to hold the approver's RSA **private** key.
3. `approve.py` is the *only* script capable of unwrapping `data_key`. It
   requires the private key **and** an explicit interactive confirmation
   (typing `APPROVE`) before it will release anything.
4. Every approval is signed (RSA-PSS) so the approval record can't be
   forged or hand-edited to fake authorization — `decrypt.py` verifies this
   signature before it will do anything.
5. `decrypt.py` refuses to run unless approval status is `APPROVED` **and**
   the signature over that approval verifies. Without a genuine approval,
   decryption is not just "discouraged" — it is mathematically impossible.

## Files

| File | Purpose |
|---|---|
| `generate_keys.py` | Generates the approver's RSA key pair |
| `generate_payload.py` | Creates a harmless test payload |
| `encrypt.py` | Encrypts the payload; wraps the data key with the approver's public key; creates a PENDING approval request |
| `approve.py` | Interactive — only this script can release the data key, and only after explicit `APPROVE` confirmation |
| `decrypt.py` | Verifies the signed approval, then decrypts the payload |

## How to run

```bash
pip install cryptography

# 1. One-time setup
python generate_keys.py
python generate_payload.py

# 2. Encrypt the payload (creates a PENDING approval request)
python encrypt.py

# 3. Try to decrypt now — this will be blocked
python decrypt.py

# 4. Approve explicitly (you must type APPROVE)
python approve.py

# 5. Decrypt again — now it succeeds
python decrypt.py
```

## What this demonstrates

- **Envelope encryption**: the data-encrypting key is itself encrypted
  (wrapped) by a key only the approver holds — the same pattern used by
  real KMS/HSM-based systems.
- **Human-in-the-loop authorization**: decryption capability doesn't exist
  until a person explicitly approves it, not just a flag being set.
- **Tamper-evidence**: the approval record is cryptographically signed, so
  editing the JSON status by hand does not grant access.

`keys/approver_private_key.pem` is generated locally by
`generate_keys.py` and must never be committed to version control or
shared — it is what makes approval meaningful.
# combination-enc
