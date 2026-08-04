#!/usr/bin/env python3
"""
Download audio from YouTube using yt_dlp, extract a clip with ffmpeg,
convert to WAV and append a metadata row to data_sources_template.csv.

Usage:
  python scripts/download_extract_youtube.py --url <URL> --start 12 --end 25 \
    --source-id yt-001 --label explosion --output-dir data/raw

Notes:
- Requires: yt-dlp, ffmpeg in PATH, Python packages: pandas (optional)
- Verify licenses before using any downloaded file (see DATA_COMPLIANCE_CHECKLIST.md)
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime
import csv

try:
    import yt_dlp
except Exception:
    print("yt_dlp not installed. Install with: pip install yt-dlp")
    yt_dlp = None


def run(cmd):
    print('RUN:', ' '.join(cmd))
    subprocess.check_call(cmd)


def download_audio(url, out_dir, tmp_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': tmp_name,
        'quiet': True,
        'no_warnings': True,
    }
    if yt_dlp is None:
        raise RuntimeError('yt_dlp Python package required')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info


def ffmpeg_extract(src_path, dst_path, start, end, sr=16000, channels=2):
    ff_cmd = [
        'ffmpeg', '-y', '-i', src_path,
    ]
    if start is not None:
        ff_cmd += ['-ss', str(start)]
    if end is not None:
        ff_cmd += ['-to', str(end)]
    ff_cmd += ['-ar', str(sr), '-ac', str(channels), dst_path]
    run(ff_cmd)


def append_metadata(csv_path, row):
    header = ['source_id','source_url','license','license_url','copyright_holder',
              'date_accessed','clip_start_s','clip_end_s','proposed_class_label','transcription_present',
              'contains_pii','consent_obtained','sensitivity_level','retention_policy','local_path','notes']
    exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True)
    p.add_argument('--start', type=float, default=None, help='start time in seconds')
    p.add_argument('--end', type=float, default=None, help='end time in seconds')
    p.add_argument('--output-dir', default='data/raw')
    p.add_argument('--source-id', default=None)
    p.add_argument('--label', default='unknown')
    p.add_argument('--license', default='unknown')
    p.add_argument('--license-url', default='')
    p.add_argument('--copyright-holder', default='')
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    tmp_basename = os.path.join(args.output_dir, 'tmp_%(id)s.%(ext)s')
    tmp_name = tmp_basename % {'id': 'yt', 'ext': '%(ext)s'}

    print('Downloading', args.url)
    info = download_audio(args.url, args.output_dir, tmp_name)
    # find downloaded file (yt_dlp writes actual filename)
    # best effort: look for files in output_dir modified in last minute
    candidates = sorted([os.path.join(args.output_dir,f) for f in os.listdir(args.output_dir)], key=os.path.getmtime, reverse=True)
    src = candidates[0]
    print('Downloaded file:', src)

    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    out_name = f"{args.source_id or 'yt'}_{int(datetime.utcnow().timestamp())}.wav"
    out_path = os.path.join(args.output_dir, out_name)

    print('Extracting clip to', out_path)
    ffmpeg_extract(src, out_path, args.start, args.end, sr=16000, channels=2)

    csv_path = 'data_sources.csv'
    row = {
        'source_id': args.source_id or f"yt-{int(datetime.utcnow().timestamp())}",
        'source_url': args.url,
        'license': args.license,
        'license_url': args.license_url,
        'copyright_holder': args.copyright_holder,
        'date_accessed': timestamp,
        'clip_start_s': args.start if args.start is not None else '',
        'clip_end_s': args.end if args.end is not None else '',
        'proposed_class_label': args.label,
        'transcription_present': 'no',
        'contains_pii': 'unknown',
        'consent_obtained': 'no',
        'sensitivity_level': 'high',
        'retention_policy': 'internal-only',
        'local_path': out_path.replace('\\','/'),
        'notes': ''
    }
    append_metadata(csv_path, row)
    print('Metadata appended to', csv_path)

if __name__ == '__main__':
    main()
