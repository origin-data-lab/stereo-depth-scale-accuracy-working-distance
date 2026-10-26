<!-- ODL_QUALITY_V2 -->

# Origin Data Lab · Technical Field Note #09

**ODL Stereo Depth-Scale Accuracy 25-90 cm**

[![GitHub](https://img.shields.io/badge/GitHub-Open-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/origin-data-lab/stereo-depth-scale-accuracy-working-distance) [![Hugging Face](https://img.shields.io/badge/Hugging_Face-Open-FFD21E?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/datasets/origin-data-lab/stereo-depth-scale-accuracy-working-distance) [![Kaggle](https://img.shields.io/badge/Kaggle-Open-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/datasets/origindatalab/odl-stereo-depth-scale-accuracy) [![Technical Note](https://img.shields.io/badge/Technical_Note-Open-0B1220?style=for-the-badge&logo=read-the-docs&logoColor=white)](https://origindatalab.io/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html)

[English technical note](https://origindatalab.io/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html) | [Korean technical note](https://origindatalab.io/ko/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html)

---

# ODL Field Note #09 — Stereo depth-scale accuracy (25–90 cm)
Reproduction code and derived measurements for Origin Data Lab Technical Field Note #09.

## What it measures
Stereo depth-scale error of a fisheye stereo+IMU rig (R8 OEM, ODL-EGO S1 configuration) against ChArUco squares measured with a steel rule.

## Reproduce
```bash
pip install opencv-contrib-python-headless==4.10.0.84 numpy pandas pyyaml matplotlib
export ODL_DATA=analysis/data          # detection JSONs + factory_calibration.yaml
PYTHONPATH=analysis python3 analysis/a1_depth_scale.py out
PYTHONPATH=analysis python3 analysis/make_figures.py out
```
`factory_calibration.yaml` is manufacturer material and is **not included**; without it the triangulation step cannot be reproduced. Detection JSONs (corner coordinates) are included.

## Outputs
| file | content |
|---|---|
| a1_per_frame.csv | one row per stereo frame: distance, tilt, image position, square size, scale error |
| a1_scale_summary.csv | medians / IQR / bootstrap CI per distance bin and edge region |
| a1_tape_holds.csv | tape-measure holds vs stereo distance with linear fit |

## Limits
Single unit, single day, automated analysis only. See methodology.md.

Licence: to be decided (candidates: MIT for code, CC BY 4.0 for CSV) — not applied yet.

---

## Explore Origin Data Lab

[![GitHub](https://img.shields.io/badge/GitHub-Open-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/origin-data-lab/stereo-depth-scale-accuracy-working-distance) [![Hugging Face](https://img.shields.io/badge/Hugging_Face-Open-FFD21E?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/datasets/origin-data-lab/stereo-depth-scale-accuracy-working-distance) [![Kaggle](https://img.shields.io/badge/Kaggle-Open-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/datasets/origindatalab/odl-stereo-depth-scale-accuracy) [![Technical Note](https://img.shields.io/badge/Technical_Note-Open-0B1220?style=for-the-badge&logo=read-the-docs&logoColor=white)](https://origindatalab.io/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html)

[Official Website](https://origindatalab.io/) | [Technical Field Notes](https://origindatalab.io/technical-field-notes/) | [English Note](https://origindatalab.io/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html) | [Korean Note](https://origindatalab.io/ko/technical-field-notes/stereo-depth-scale-accuracy-working-distance.html)

[GitHub](https://github.com/origin-data-lab/stereo-depth-scale-accuracy-working-distance) | [Hugging Face](https://huggingface.co/datasets/origin-data-lab/stereo-depth-scale-accuracy-working-distance) | [Kaggle Dataset](https://www.kaggle.com/datasets/origindatalab/odl-stereo-depth-scale-accuracy) | [Kaggle Notebook](https://www.kaggle.com/code/origindatalab/stereo-depth-scale-accuracy-working-distance)
