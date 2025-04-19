from cryptography.fernet import Fernet

# Generate and print encryption key
key = Fernet.generate_key()
print(f"🔑 Encryption Key (save this securely!):\n{key.decode()}")

fernet = Fernet(key)

# Your plaintext credentials
username = "user_name"
password = "Password"

# Encrypt
encrypted_username = fernet.encrypt(username.encode()).decode()
encrypted_password = fernet.encrypt(password.encode()).decode()

print(f"🔐 Encrypted Username:\n{encrypted_username}")
print(f"🔐 Encrypted Password:\n{encrypted_password}")
