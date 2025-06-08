from setuptools import setup, find_packages

setup(
    name='email_notify',
    version='1.0.1',
    description='Email notifications when a code block or function finishes or ends unexpectedly',
    long_description='',
    long_description_content_type='text/markdown',
    author='Chao-Ning Hu',
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
    ],
    install_requires=[
        'cryptography',
    ],
)
