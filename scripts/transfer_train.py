#!/usr/bin/env python3
"""
Transfer-learning skeleton for SemanticHearing-based model.
- Loads processed dataset from data/processed (segments.csv)
- Loads pretrained checkpoint (PyTorch) and replaces/fine-tunes classifier head
- Saves checkpoints to experiments/finetune

This is a template: adjust model loading API to match SemanticHearing codebase.
"""
import argparse
import os
import yaml
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np

# Simple dataset wrapper for segments.csv
class SegmentsDataset(Dataset):
    def __init__(self, csv_path, transform=None):
        self.df = pd.read_csv(csv_path)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        wav_path = row['segment_path']
        # lightweight reader
        import soundfile as sf
        y, sr = sf.read(wav_path)
        # ensure mono
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        y = torch.from_numpy(y).float()
        label = row.get('label', 'unknown')
        return y, label


def build_model(num_classes, device, pretrained_ckpt=None):
    # Placeholder: replace with actual SemanticHearing model import
    # from src.models.waveformer import Waveformer
    class Dummy(nn.Module):
        def __init__(self, nc):
            super().__init__()
            self.backbone = nn.Sequential(nn.Conv1d(1,16,3), nn.ReLU(), nn.AdaptiveAvgPool1d(1))
            self.classifier = nn.Linear(16, nc)
        def forward(self, x):
            if x.dim()==1:
                x = x.unsqueeze(0)
            x = x.unsqueeze(1)  # (B,1,T)
            f = self.backbone(x).squeeze(-1)
            return self.classifier(f)
    model = Dummy(num_classes)
    if pretrained_ckpt and os.path.exists(pretrained_ckpt):
        try:
            ck = torch.load(pretrained_ckpt, map_location='cpu')
            # adapt loading to checkpoint format
            model.load_state_dict(ck, strict=False)
            print('Loaded pretrained weights (best effort)')
        except Exception as e:
            print('Pretrained load skipped:', e)
    return model.to(device)


def label_to_index(labels):
    return {l:i for i,l in enumerate(labels)}


def train(cfg_path):
    cfg = yaml.safe_load(open(cfg_path))
    device = torch.device(cfg.get('device','cuda' if torch.cuda.is_available() else 'cpu'))
    labels = [l.strip() for l in open(cfg['classes_file']).read().splitlines() if l.strip()]
    lab2idx = label_to_index(labels)
    num_classes = len(labels)
    model = build_model(num_classes, device, cfg.get('pretrained_ckpt'))

    dataset = SegmentsDataset(cfg['data_csv'])
    batch_size = int(cfg.get('batch_size', 32))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    lr = float(cfg.get('lr', 1e-4))
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    out_dir = cfg.get('output_dir','experiments/finetune')
    os.makedirs(out_dir, exist_ok=True)

    for epoch in range(cfg.get('epochs',5)):
        model.train()
        total_loss = 0.0
        for i, (x, y) in enumerate(dataloader):
            # naive preprocessing: pad/trim to fixed length
            # convert labels
            y_idx = torch.tensor([lab2idx.get(lbl, lab2idx.get('unknown',0)) for lbl in y])
            # ensure tensor shape
            if x.dim()==1:
                x = x.unsqueeze(0)
            x = x.to(device)
            y_idx = y_idx.to(device)
            logits = model(x)
            loss = criterion(logits, y_idx)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg = total_loss / (i+1)
        print(f'Epoch {epoch+1}/{cfg.get("epochs",5)} avg_loss={avg:.4f}')
        # save checkpoint
        torch.save(model.state_dict(), os.path.join(out_dir, f'ckpt_epoch_{epoch+1}.pt'))

    # optional ONNX export
    if cfg.get('export_onnx'):
        dummy = torch.randn(1, int(cfg.get('dummy_wave_len',16000))).to(device)
        try:
            torch.onnx.export(model, dummy, os.path.join(out_dir,'model.onnx'), opset_version=11)
            print('Exported ONNX to', out_dir)
        except Exception as e:
            print('ONNX export failed:', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='scripts/train_config_template.yaml')
    args = parser.parse_args()
    train(args.config)
