#!/usr/bin/env python3
"""
Preprocessing pipeline template.
- Scans input_dir for wav files (recursively)
- Resamples to target_sr, converts to mono or preserves channels
- Segments into fixed-length windows with overlap
- Normalizes per-segment RMS
- Optional augmentations: add_noise (SNR), time_shift, pitch_shift (librosa)
- Writes segments to output_dir/<class_label>/<origfile>__start_end.wav
- Appends segment rows to a csv (segments.csv) with provenance

Usage (dry-run default):
  python scripts/preprocess_pipeline.py --input data/raw --out data/processed --sr 16000 --seg_len 1.0 --overlap 0.5 --dry_run

NOTE: This is a template. Install dependencies: pip install soundfile numpy librosa resampy
"""
import argparse
import os
import soundfile as sf
import numpy as np
import csv
from datetime import datetime

try:
    import librosa
except Exception:
    librosa = None


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def list_wavs(root):
    exts = ('.wav', '.flac', '.mp3', '.ogg')
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(exts):
                yield os.path.join(dirpath, fn)


def rms(y):
    return np.sqrt(np.mean(y**2) + 1e-12)


def normalize_audio(y, target_rms=0.1):
    r = rms(y)
    if r == 0:
        return y
    return y * (target_rms / r)


def resample_audio(y, orig_sr, target_sr):
    if orig_sr == target_sr:
        return y
    if librosa is None:
        raise RuntimeError('librosa required for resampling (pip install librosa)')
    return librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)


def time_shift(y, sr, shift_seconds):
    shift = int(shift_seconds * sr)
    return np.roll(y, shift)


def pitch_shift(y, sr, n_steps):
    if librosa is None:
        raise RuntimeError('librosa required for pitch_shift')
    return librosa.effects.pitch_shift(y, sr, n_steps)


def add_noise(y, snr_db):
    sig_rms = rms(y)
    snr = 10 ** (snr_db / 20.0)
    noise_rms = sig_rms / snr
    noise = np.random.normal(0, noise_rms, size=y.shape)
    return y + noise


def write_segment(out_path, y, sr):
    ensure_dir(os.path.dirname(out_path))
    sf.write(out_path, y, sr)


def append_segments_csv(csv_path, rows):
    header = ['segment_path','orig_file','start_s','end_s','label','source_url','date_created']
    exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def process_file(fp, args, segments_rows):
    info = sf.info(fp)
    data, sr = sf.read(fp, always_2d=True)
    # convert to mono by averaging channels for model training; keep option
    if args.keep_channels:
        # preserve channels as columns
        y = data.T  # shape (channels, samples)
        # For segmentation we take mean across channels if multi-channel not supported
        mono = np.mean(y, axis=0)
    else:
        mono = np.mean(data, axis=1)
    # resample
    if sr != args.sr:
        mono = resample_audio(mono.astype(np.float32), sr, args.sr)
        sr = args.sr
    total_seconds = len(mono) / sr
    step = args.seg_len * (1 - args.overlap)
    starts = np.arange(0, max(0, total_seconds - args.seg_len) + 1e-6, step)
    for s in starts:
        e = s + args.seg_len
        start_sample = int(s * sr)
        end_sample = int(e * sr)
        seg = mono[start_sample:end_sample]
        if len(seg) < int(args.seg_len * sr):
            # pad
            pad_len = int(args.seg_len * sr) - len(seg)
            seg = np.pad(seg, (0, pad_len))
        # normalize
        seg = normalize_audio(seg, target_rms=args.target_rms)
        seg_variants = [(seg, 'orig')]
        # augmentations
        if args.augment:
            if args.time_shift and args.time_shift != 0:
                seg_variants.append((time_shift(seg, sr, args.time_shift), 'time_shift'))
            if args.pitch_shift and args.pitch_shift != 0:
                if librosa is None:
                    print('Warning: librosa missing; pitch_shift skipped')
                else:
                    seg_variants.append((pitch_shift(seg, sr, args.pitch_shift), 'pitch_shift'))
            if args.noise_snr is not None:
                seg_variants.append((add_noise(seg, args.noise_snr), f'noise_{args.noise_snr}dB'))
        for idx, (sdata, tag) in enumerate(seg_variants):
            rel_dir = os.path.relpath(os.path.dirname(fp), args.input)
            label = infer_label_from_path(fp, args)
            out_dir = os.path.join(args.out, label)
            base = os.path.splitext(os.path.basename(fp))[0]
            out_name = f"{base}__{int(s*1000)}_{int(e*1000)}_{tag}.wav"
            out_path = os.path.join(out_dir, out_name)
            if args.dry_run:
                print('DRY:', out_path)
            else:
                write_segment(out_path, sdata, sr)
            rows = {
                'segment_path': out_path.replace('\\','/'),
                'orig_file': fp.replace('\\','/'),
                'start_s': s,
                'end_s': e,
                'label': label,
                'source_url': '',
                'date_created': datetime.utcnow().isoformat()+'Z'
            }
            segments_rows.append(rows)


def infer_label_from_path(fp, args):
    # simple heuristic: parent folder name as label if matches CLASSES.yaml; else "unknown"
    parent = os.path.basename(os.path.dirname(fp))
    # TODO: load CLASSES.yaml to verify membership; simplified here
    return parent if parent else 'unknown'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--sr', type=int, default=16000)
    p.add_argument('--seg_len', type=float, default=1.0)
    p.add_argument('--overlap', type=float, default=0.5)
    p.add_argument('--augment', action='store_true')
    p.add_argument('--time_shift', type=float, default=0.0, help='seconds to shift')
    p.add_argument('--pitch_shift', type=float, default=0.0, help='n_steps for pitch_shift')
    p.add_argument('--noise_snr', type=float, default=None, help='additive noise SNR in dB')
    p.add_argument('--dry_run', action='store_true', default=False, help='do not write files (default: write files)')
    p.add_argument('--keep_channels', action='store_true', default=False)
    p.add_argument('--target_rms', type=float, default=0.1)
    args = p.parse_args()

    args.input = os.path.abspath(args.input)
    args.out = os.path.abspath(args.out)
    ensure_dir(args.out)

    segments_rows = []
    for fp in list_wavs(args.input):
        try:
            process_file(fp, args, segments_rows)
        except Exception as e:
            print('ERROR processing', fp, e)

    csv_path = os.path.join(args.out, 'segments.csv')
    if not args.dry_run:
        append_segments_csv(csv_path, segments_rows)
    else:
        print('DRY_RUN: segments to be written:', len(segments_rows))

if __name__ == '__main__':
    main()
