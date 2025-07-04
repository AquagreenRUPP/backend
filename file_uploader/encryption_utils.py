import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import json

class EncryptionManager:
    def __init__(self):
        self.key = self._get_encryption_key()
        self.fernet = Fernet(self.key)
    
    def _get_encryption_key(self):
        password = settings.SECRET_KEY.encode()
        salt = b'genetic_data_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_file(self, file_content):
        if isinstance(file_content, str):
            file_content = file_content.encode()
        return self.fernet.encrypt(file_content)
    
    def decrypt_file(self, encrypted_content):
        return self.fernet.decrypt(encrypted_content)
    
    def encrypt_text(self, text):
        if not text:
            return text
        return base64.urlsafe_b64encode(
            self.fernet.encrypt(text.encode())
        ).decode()
    
    def decrypt_text(self, encrypted_text):
        if not encrypted_text:
            return encrypted_text
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            return self.fernet.decrypt(encrypted_bytes).decode()
        except:
            return encrypted_text
    
    def encrypt_json(self, data):
        json_str = json.dumps(data)
        return self.encrypt_text(json_str)
    
    def decrypt_json(self, encrypted_data):
        decrypted_str = self.decrypt_text(encrypted_data)
        try:
            return json.loads(decrypted_str)
        except:
            return decrypted_str

encryption_manager = EncryptionManager()