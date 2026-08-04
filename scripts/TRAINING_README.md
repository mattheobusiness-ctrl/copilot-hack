Transfer Learning & Evaluation README

Files created:
- scripts/transfer_train.py — transfer-learning skeleton (template)
- scripts/evaluate_model.py — evaluation skeleton (template)
- scripts/train_config_template.yaml — config skeleton; update paths before running

Quick steps (offline, templates only):
1) Prepare processed dataset: run preprocess_pipeline.py to create data/processed/segments.csv
2) Edit train_config_template.yaml: set data_csv, classes_file, pretrained_ckpt, output_dir, epochs, batch_size
3) Run training (dry-run/adjust code first):
   python scripts/transfer_train.py --config scripts/train_config_template.yaml

Notes:
- transfer_train.py is deliberately generic. Adapt model loading to the SemanticHearing model API in src/ (e.g., import model class, load checkpoint, match state dict keys).
- Use GPU/Jetson for real training; for Jetson, prefer small batches and TensorRT for deployment.
- Evaluate with scripts/evaluate_model.py after training; replace the placeholder inference with the actual model.predict implementation.
