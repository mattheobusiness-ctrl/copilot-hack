#!/usr/bin/env python3
"""
Template to prepare FSD50K download steps.
FSD50K audio is large; this script instructs how to fetch metadata and audio lists.
"""
print('FSD50K preparation template')
print('\nSteps:')
print('1) Download metadata (manifest) from: https://zenodo.org/ (FSD50K release page)')
print('2) Use manifest to selectively download clips or request full archive if available.')
print('3) Keep provenance: record source IDs and license in data_sources_template.csv')

print('\nExample (manual):\nwget -O fsd50k_metadata.zip <metadata_url>\n# then inspect manifests and download audio archives as provided')
