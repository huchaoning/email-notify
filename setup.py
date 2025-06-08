from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='email_notify',
    version='1.0.2',
    description='Email notifications when a code block or function finishes or ends unexpectedly',
    long_description=long_description,
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
