#!/usr/bin/env python3
"""
Template to download UrbanSound8K. Script prints commands; run manually after license check.
"""
OUT_DIR = 'data/urbansound8k'
URL = 'https://zenodo.org/record/1203745/files/UrbanSound8K.tar.gz'

print('UrbanSound8K download template')
print('URL:', URL)
print('\nRun manually:')
print(f"mkdir -p {OUT_DIR} && wget -O urbansound8k.tar.gz '{URL}' && tar -xzf urbansound8k.tar.gz -C {OUT_DIR}")
print('\nMap relevant classes (e.g., siren, horn, vehicle) into CLASSES.yaml as needed.')
