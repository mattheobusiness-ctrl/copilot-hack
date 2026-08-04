Dataset Acquisition README

This folder contains templates to prepare and download public audio datasets. NONE of these scripts download data automatically — they are templates and safety wrappers.

How to proceed safely:
1) Review DATA_COMPLIANCE_CHECKLIST.md and ensure legal clearance.
2) Choose which datasets to fetch (we prepared templates for ESC-50, UrbanSound8K, FSD50K, Freesound, AudioSet).
3) For Freesound: obtain API key and prefer CC0/CC-BY clips.
4) For AudioSet: use prepared id lists and CONFIRM before invoking yt-dlp to pull YouTube audio.
5) After downloading: run processing scripts (segmentation, resampling, normalization, metadata append).

Ask the assistant to run any specific template command; explicit approval required before any network activity.
