# First-party synthetic research data

`generate_layout_dataset.py` renders fictitious VeriVision research credentials, visibly marked `SAMPLE / NOT VALID FOR IDENTIFICATION`. It emits image files plus token quadrilaterals and BIOES entity labels for LayoutLMv3 experiments.

Example:

```text
python synthetic_data/generate_layout_dataset.py --output-dir /content/verivision-data/synthetic-layout-v1 --count 500 --seed 42
```

Never modify it to reproduce government-issued credentials, official logos, valid document-number formats, real identities, or security features.
