content = (
    "This is a harmless simulated test payload.\n"
    "It exists only to demonstrate encryption + approval-gated decryption.\n"
    "It contains no real, sensitive, or executable content.\n"
)

with open("payload/test_payload.txt", "w") as f:
    f.write(content)

print("Test payload created -> payload/test_payload.txt")

