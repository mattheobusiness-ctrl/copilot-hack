#!/usr/bin/env python3
"""
Create per-class sampling lists from dataset manifests without downloading.
- Inputs: manifests in data/manifests/ (CSV or JSON), CLASSES.yaml, data/dataset_class_mapping.yaml
- Outputs: data/sampling/<class>.txt with one ID or path per line

This is a dry-run friendly script: it will not perform any downloads. It only filters manifest rows by mapping rules.
"""
import os
import yaml
import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MANIFEST_DIR = os.path.join(BASE, 'data', 'manifests')
OUT_DIR = os.path.join(BASE, 'data', 'sampling')
ensure = lambda p: os.makedirs(p, exist_ok=True)
ensure(OUT_DIR)

# Load classes
with open(os.path.join(BASE, 'CLASSES.yaml')) as f:
    classes_yaml = yaml.safe_load(f)
TARGET_CLASSES = classes_yaml.get('classes', [])

# Load dataset->class mapping
mapping_path = os.path.join(BASE, 'data', 'dataset_class_mapping.yaml')
if os.path.exists(mapping_path):
    dmap = yaml.safe_load(open(mapping_path))
else:
    dmap = {}

# Helper to append candidate
def append_candidate(cls, candidate):
    out_file = os.path.join(OUT_DIR, f'{cls}.txt')
    with open(out_file, 'a', encoding='utf-8') as f:
        f.write(candidate + '\n')

# Process known manifests
# ESC-50: expects a csv with 'filename','category'
esc50_manifest = os.path.join(MANIFEST_DIR, 'esc50.csv')
if os.path.exists(esc50_manifest):
    df = pd.read_csv(esc50_manifest)
    esc_map = dmap.get('esc50', {}).get('mappings', {})
    for _, row in df.iterrows():
        cat = row.get('category')
        cls = esc_map.get(cat)
        if cls in TARGET_CLASSES:
            candidate = os.path.join('esc50', row.get('filename'))
            append_candidate(cls, candidate)

# UrbanSound8K manifest: expects 'slice_file_name','class'
urb_manifest = os.path.join(MANIFEST_DIR, 'urbansound8k.csv')
if os.path.exists(urb_manifest):
    df = pd.read_csv(urb_manifest)
    urb_map = dmap.get('urbansound8k', {}).get('mappings', {})
    for _, row in df.iterrows():
        cat = row.get('class')
        cls = urb_map.get(cat)
        if cls in TARGET_CLASSES:
            candidate = os.path.join('urbansound8k', row.get('slice_file_name'))
            append_candidate(cls, candidate)

# FSD50K manifest: expects 'fname','labels'
fsd_manifest = os.path.join(MANIFEST_DIR, 'fsd50k_meta.csv')
if os.path.exists(fsd_manifest):
    df = pd.read_csv(fsd_manifest)
    fsd_map = dmap.get('fsd50k', {}).get('mappings', {})
    for _, row in df.iterrows():
        labels = str(row.get('labels'))
        for key, cls in fsd_map.items():
            if key in labels and cls in TARGET_CLASSES:
                candidate = row.get('fname')
                append_candidate(cls, candidate)

# AudioSet / other manifests: generic handling for CSVs with 'youtube_id' and 'label'
for fname in os.listdir(MANIFEST_DIR) if os.path.exists(MANIFEST_DIR) else []:
    if fname.lower().endswith('.csv') and fname not in ('esc50.csv','urbansound8k.csv','fsd50k_meta.csv'):
        path = os.path.join(MANIFEST_DIR, fname)
        try:
            df = pd.read_csv(path)
            if 'youtube_id' in df.columns and 'label' in df.columns:
                # map labels via mapping file if available
                aud_map = dmap.get('audioset', {}).get('mappings', {})
                for _, row in df.iterrows():
                    lab = row.get('label')
                    cls = aud_map.get(lab)
                    if cls in TARGET_CLASSES:
                        # store as youtube_id|start|end if present
                        start = row.get('start_time','')
                        end = row.get('end_time','')
                        yid = row.get('youtube_id')
                        candidate = f"{yid}|{start}|{end}"
                        append_candidate(cls, candidate)
        except Exception as e:
            print('Skipping manifest', fname, e)

# Summary
for cls in TARGET_CLASSES:
    f = os.path.join(OUT_DIR, f'{cls}.txt')
    count = 0
    if os.path.exists(f):
        with open(f,'r',encoding='utf-8') as fh:
            count = sum(1 for _ in fh)
    print(f'Class {cls}: {count} candidates')

print('Sampling lists created (dry-run: only lists). Review data/sampling/*.txt')
