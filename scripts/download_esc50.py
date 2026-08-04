#!/usr/bin/env python3
"""
Download and extract ESC-50 dataset (template).
This script will only show the wget command and not run it automatically.
Edit and run manually after reviewing license and confirming.
"""
import os

ESC50_URL = 'https://github.com/karoldvl/ESC-50/archive/master.zip'
OUT_DIR = 'data/esc50'

print('ESC-50 download template')
print('URL:', ESC50_URL)
print('\nRun manually after review:')
print(f"mkdir -p {OUT_DIR} && wget -O esc50.zip {ESC50_URL} && unzip esc50.zip -d {OUT_DIR}")

print('\nNote: ESC-50 is usable for ambient/military-ambient sounds; map classes to CLASSES.yaml as needed.')
