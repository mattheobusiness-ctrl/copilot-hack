Preprocessing pipeline (template)

Files:
- preprocess_pipeline.py: segments, resamples, normalizes, optional augmentations. Runs in dry-run mode by default to avoid accidental writes.

Quick start (dry-run):
  python scripts/preprocess_pipeline.py --input data/raw --out data/processed --sr 16000 --seg_len 1.0 --overlap 0.5 --dry_run

To actually write files, omit --dry_run. Be sure to inspect outputs and the generated segments.csv in the output folder.

Dependencies (install before running for real):
  pip install soundfile numpy librosa resampy

Notes:
- The script infers class labels from the parent folder name of each audio file. Place raw clips under data/raw/<class_label>/...
- Augmentations are simple examples; tune values for pitch/time/noise according to training needs.
- Keep a copy of original files; do not overwrite raw data.
