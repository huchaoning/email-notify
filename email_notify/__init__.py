import os
import json
import base64
from getpass import getpass

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from functools import wraps
from contextlib import contextmanager

from ._crypt import encrypt, decrypt, cpuid


CONFIG_PATH = os.path.expanduser('~/.email_notify.config')
_config_cache = None



def _save_auth_config():
    config = _load_config()
    keep = {}
    if 'email' in config:
        keep['email'] = config['email']
    if 'password' in config:
        keep['password'] = config['password']

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            raw = json.load(f)
    else:
        raw = {}
    raw.update(keep)

    with open(CONFIG_PATH, 'w') as f:
        json.dump(raw, f, indent=4)



def _save_smtp_config():
    config = _load_config()
    keep = {}
    for k in ['smtp_host', 'smtp_port']:
        if k in config:
            keep[k] = config[k]

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            raw = json.load(f)
    else:
        raw = {}
    raw.update(keep)

    with open(CONFIG_PATH, 'w') as f:
        json.dump(raw, f, indent=4)



def _load_config():
    global _config_cache
    if _config_cache is None:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                _config_cache = json.load(f)
        else:
            _config_cache = {}
    return _config_cache



def auth(save=False):
    config = _load_config()

    email_enc = encrypt(input('Email address: ').strip(), cpuid())
    passwd_enc = encrypt(getpass('Application password: ').strip(), cpuid())

    config['email'] = base64.b64encode(email_enc).decode()
    config['password'] = base64.b64encode(passwd_enc).decode()

    if save:
        _save_auth_config()



def smtp(save=False):
    config = _load_config()

    smtp_host = input('SMTP Host: ').strip()
    smtp_port_str = input('SMTP Port: ').strip()

    if not smtp_port_str.isdigit():
        raise ValueError(f"Invalid SMTP Port: '{smtp_port_str}'")

    smtp_port = int(smtp_port_str)

    config.update({
        'smtp_host': smtp_host,
        'smtp_port': smtp_port,
    })

    if save:
        _save_smtp_config()



def forget():
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
        print('done')
    else:
        print(f"token '{CONFIG_PATH}' not exists")



def send(subject, message, recipient):
    config = _load_config()

    for key in ['email', 'password', 'smtp_host', 'smtp_port']:
        if key not in config:
            raise ValueError(f"Missing '{key}' in config. Run `email_notify.auth()` or `email_notify.smtp()` to configure.")

    sender = decrypt(base64.b64decode(config['email']), cpuid())
    password = decrypt(base64.b64decode(config['password']), cpuid())
    smtp_host = config['smtp_host']
    smtp_port = config['smtp_port']

    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = formataddr([f'email_notify', sender])
    msg['To'] = recipient
    msg['Subject'] = subject

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()



@contextmanager
def context(recipient, task_name='Task'):
    try:
        yield
        send(f"{task_name} Completed", f"Your task '{task_name}' completed successfully.", recipient)
    except Exception as e:
        send(f"{task_name} Error", f"Your task '{task_name}' failed with error: {e}", recipient)
        raise



def decorator(recipient):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            with context(recipient, task_name=func.__name__):
                return func(*args, **kwargs)
        return inner
    return wrapper




