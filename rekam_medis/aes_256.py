from cryptography.fernet import Fernet

# Generate a random key
def generate_key():
    return Fernet.generate_key()

# Encrypt a file
def encrypt_file(filename, output_file, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(output_file, 'wb') as file:
        file.write(encrypted_data)

# Decrypt a file
def decrypt_file(filename, key):
    fernet = Fernet(key)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    return fernet.decrypt(encrypted_data)