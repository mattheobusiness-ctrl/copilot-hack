Sampling Plan — Auswahl freier Datenclip‑Kandidaten für Klassen

Ziel
- Für jede Klasse in CLASSES.yaml eine initiale Auswahl von Kandidaten erstellen (IDs oder Pfade), ohne Download.
- Priorität: freie/lizenzierbare Quellen (ESC-50, UrbanSound8K, FSD50K, Freesound, AudioSet). 

Mengen & Priorisierung
- Ziel pro Klasse (Initial): 500 Clips (wenn verfügbar). Minimum für prototype: 50–100 Clips/Klasse.
- Priorität bei Quelle: FSD50K (groß) > AudioSet (reich) > Freesound (gezielt, CC0/CC-BY) > UrbanSound8K/ESC-50 (klein, nützlich für Umgebungslaute).

Auswahlkriterien
- Lizenz: nur CC0/CC-BY oder klar erlaubte Nutzung (AudioSet/YouTube nur IDs, rechtliche Prüfung später).
- Dauer: 0.5–10s (bevorzugt 0.5–3s für Klassifikation); lange Clips segmentieren.
- SNR & Klarheit: falls Metadaten vorhanden, bevorzugen höhere Signal‑to‑Noise; sonst manuelle Stichprobe.
- Einzigartigkeit: vermeide Duplikate über Quellen.

Vorgehen (technisch)
1) Lade Manifeste/CSV (manifest des jeweiligen Datasets) lokal in data/manifests/ (ESC-50, UrbanSound8K, FSD50K, AudioSet).  
2) Verwende scripts/create_sampling_lists.py (Dry‑Run) um pro Klasse eine candidate‑Liste zu erzeugen in data/sampling/*.txt.  
3) Prüfe stichprobenartig 20 Einträge/Klasse (manuell) und markiere schlechte Kandidaten in data/sampling/rejects.csv.  
4) Nach Freigabe: Download‑Phase (separat, explicit) — yt‑dl/ffmpeg oder Freesound API.

Output
- data/sampling/<class>.txt  (Liste von IDs oder Pfaden, ein Eintrag pro Zeile)
- data/sampling/summary.md  (counts per class)

Sicherheits-/Compliance‑Hinweis
- Keine Downloads aus YouTube/AudioSet ohne Compliance‑Go. Dieser Plan erzeugt zunächst nur ID‑Listen.

Nächste Schritte (autonom)
- Erzeuge die candidate‑Listen mit scripts/create_sampling_lists.py (Dry‑Run).
- Generiere data/sampling/summary.md mit Verfügbarkeiten pro Klasse.
