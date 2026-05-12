# Email Notify

[![PyPI version](https://img.shields.io/pypi/v/email-notify.svg)](https://pypi.org/project/email-notify/)
[![Python Version](https://img.shields.io/badge/python-3%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/huchaoning/email-notify?color=blue)](https://github.com/huchaoning/email-notify/blob/main/LICENSE)

Email notifications when a code block or function finishes or ends unexpectedly.

Use SMTP service.

## Configuration

Before using, you need to configure your email account and SMTP server.

```python
import email_notify

# Set email address and application password (will be encrypted and saved if save=True)
email_notify.auth(save=True)

# Set SMTP server host and port (will be saved if save=True)
email_notify.smtp(save=True)
```

Configuration is saved in `$HOME/.email_notify.config`. Call `forget()` to remove the saved configuration.

## Usage

You can use `email_notify` in three ways: 

- As a context manager (recommended)
- As a decorator
- Calling `email_notify.send(subject, message, recipient)` directly

### Context Manager (recommended)

```python
import email_notify

recipient = 'user@example.com'

with email_notify.context(recipient, task_name='Task'):
    print('Running some tasks...')
    # some tasks
```

### Decorator

```python
import email_notify

recipient = 'user@example.com'

@email_notify.decorator(recipient)
def my_task():
    print('Running some tasks...')
    # some tasks

my_task()
```

### Direct Send

```python
import email_notify

recipient = 'user@example.com'

try:
    print('Running some tasks...')
    # some tasks
except Exception as e:
    subject = 'Task Failed'
    message = f'The task failed with error:\n{e}'
    email_notify.send(subject, message, recipient)
else:
    subject = 'Task Completed'
    message = f'The task finished successfully.\nResult: {result}'
    email_notify.send(subject, message, recipient)
```

## Installation

```bash
pip install email_notify
```

## Requirements

- cryptography

## Note

Make sure you know your SMTP service host and port before configuring.

Known SMTP service hosts and ports (updated 2025-6-8):

| Provider | SMTP Host   | SMTP Port  |
| -------- | ----------- | ---------- |
| QQ Mail  | smtp.qq.com | 465 or 587 |

For other providers, please refer to your email service documentation or contact your administrator.