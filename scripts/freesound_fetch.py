#!/usr/bin/env python3
"""
Fetch clips from Freesound using the Freesound API (template).
Requires FREESOUND_API_KEY env var with a valid token. This script will NOT run downloads until you set the key and confirm.
"""
import os
import requests

API_HOST = 'https://freesound.org/apiv2'
API_KEY = os.environ.get('FREESOUND_API_KEY')

if not API_KEY:
    print('FREESOUND_API_KEY not set. Export it and re-run. Example: export FREESOUND_API_KEY="YOUR_KEY"')
    print('This script is a template; no downloads will be performed until key is set and you confirm.')
    exit(0)

print('Template ready: will search Freesound for query and download matching clips (with license check).')
print('Example usage: set API key, adapt query terms ("explosion", "helicopter"), and run with care.')

# Pseudocode snippet
print('\nPseudocode:')
print('1) /search/text?query=explosion&filter=duration:[0.5 TO 10]')
print('2) For each result: check license (CC0/CC-BY), then download previews or original file via download link')
print('3) Append metadata to data_sources.csv (use data_sources_template.csv header).')
