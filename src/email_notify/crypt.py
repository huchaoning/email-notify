import os
import base64
import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

import hashlib
import subprocess
import platform


def _fingerprint_windows():
    try:
        disk_sn = subprocess.check_output('wmic diskdrive get serialnumber', shell=True).decode().strip().split('\n')[1]
        machine_id = subprocess.check_output('reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid', shell=True).decode().strip().split('    ')[-1]
        
        hardware_info = f'{machine_id}|{disk_sn}'
        return hashlib.sha256(hardware_info.encode()).hexdigest()
    except Exception as e:
        print(f'Failed to get hardware info (Windows): {e}')
        return None


def _fingerprint_macos():
    try:
        hw_uuid = subprocess.check_output("system_profiler SPHardwareDataType | grep 'Hardware UUID'", shell=True).decode().strip().split(':')[1].strip()
        disk_uuid = subprocess.check_output("system_profiler SPStorageDataType | grep 'Volume UUID' | head -n 1", shell=True).decode().strip().split(':')[1].strip()

        hardware_info = f'{hw_uuid}|{disk_uuid}'
        return hashlib.sha256(hardware_info.encode()).hexdigest()
    except Exception as e:
        print(f'Failed to get hardware info (macOS): {e}')
        return None


def _fingerprint_linux():
    try:
        machine_id = subprocess.check_output('cat /etc/machine-id', shell=True).decode().strip()
        disk_uuid = subprocess.check_output('lsblk -o NAME,UUID | grep \'sda\' | awk \'{print $2}\'', shell=True).decode().strip()

        hardware_info = f'{machine_id}|{disk_uuid}'
        return hashlib.sha256(hardware_info.encode()).hexdigest()
    except Exception as e:
        print(f'Failed to get hardware info (Linux): {e}')
        return None


def device_fingerprint():
    system = platform.system().lower()

    if system == 'windows':
        return _fingerprint_windows()
    elif system == 'darwin':
        return _fingerprint_macos()
    elif system == 'linux':
        return _fingerprint_linux()
    else:
        return None


def device_fingerprint():
    system = platform.system().lower()

    if system == 'windows':
        return _fingerprint_windows()
    elif system == 'darwin':
        return _fingerprint_macos()
    elif system == 'linux':
        return _fingerprint_linux()
    else:
        return None


# Internal function to derive the encryption key from the password
def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a key from the password using PBKDF2-HMAC-SHA256.

    Args:
        password (str): The password used to derive the key.
        salt (bytes): The salt value added to the password to prevent rainbow table attacks.

    Returns:
        bytes: The derived encryption key (32 bytes).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # Using SHA-256 as the hash algorithm
        length=32,                  # The length of the derived key (32 bytes)
        salt=salt,
        iterations=2_000_000,       # Number of iterations (to slow down brute force)
    )
    key = kdf.derive(password.encode())  # Derive the key from the password
    return key


def _isNone(password):
    if password is None:
        return getpass.getpass('input password: ')
    else:
        return password


def encrypt(message: str | bytes, password: str = None) -> bytes:
    """
    Encrypts a message using a password and a random salt.

    Args:
        message (str | bytes): The message to be encrypted (can be a string or bytes).
        password (str): The password used to derive the encryption key.

    Returns:
        bytes: The encrypted message concatenated with the salt (used for decryption).
    """
    if isinstance(message, str):
        message = message.encode()  # Convert string to bytes
    
    salt = os.urandom(16)  # Generate a 16-byte random salt
    key = _derive_key(_isNone(password), salt)  # Derive the encryption key from the password and salt
    f = Fernet(base64.urlsafe_b64encode(key))  # Create a Fernet object using the derived key
    encrypted_message = f.encrypt(message)  # Encrypt the message
    return salt + encrypted_message  # Return the salt and the encrypted message


def decrypt(encrypted_message: bytes, password: str = None) -> str | bytes:
    """
    Decrypts an encrypted message using a password and the provided salt.

    Args:
        encrypted_message (bytes): The encrypted message concatenated with the salt.
        password (str): The password used to derive the encryption key.

    Returns:
        str | bytes: The decrypted plaintext message (either a string or binary data).
    """
    salt = encrypted_message[:16]  # Extract the salt from the encrypted data
    encrypted_message = encrypted_message[16:]  # Extract the actual encrypted message
    key = _derive_key(_isNone(password), salt)  # Derive the encryption key from the password and salt
    f = Fernet(base64.urlsafe_b64encode(key))  # Create a Fernet object using the derived key
    
    try:
        # Try to decode as a string (for text files)
        return f.decrypt(encrypted_message).decode()  # Try to return as string
    except UnicodeDecodeError:
        # If decoding fails, return the original binary data
        return f.decrypt(encrypted_message)  # If it's binary data, return the raw binary data
