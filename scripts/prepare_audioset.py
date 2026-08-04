#!/usr/bin/env python3
"""
Prepare AudioSet ID lists and mapping to CLASSES.yaml.
This script downloads (or instructs to download) AudioSet manifest CSVs and creates per-class youtube_id lists.
It does NOT download YouTube audio — that requires separate, explicit step.
"""
print('AudioSet preparation template')
print('\nSteps:')
print('1) Download AudioSet CSVs (youtube_id and class annotations) from the AudioSet release page.')
print('2) Filter rows by target classes (map to CLASSES.yaml) and output text files of youtube_id per class.')
print('3) Store id lists in data/audioset_ids/<class>.txt for later yt-dlp processing (explicit approval needed).')

print('\nExample (manual):\npython -c "import pandas as pd; df = pd.read_csv(\'balanced_train_segments.csv\'); df[df.label==\'Explosion\'].youtube_id.to_csv(\'explosion_ids.txt\', index=False, header=False)"')
