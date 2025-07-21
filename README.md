<p align="center">
  <img src="img/MorphoMeasure.png" alt="MorphoMeasure banner" width="1000"/>
</p>


Python Package & CLI Wrapper for L-Measure

![CI](https://github.com/Masood-Akram/MorphoMeasure/actions/workflows/python-package.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/morphomeasure.svg)](https://pypi.org/project/morphomeasure/)
[![PyPI version](https://img.shields.io/pypi/v/morphomeasure.svg)](https://pypi.org/project/morphomeasure/)


*MorphoMeasure* is a Python package and command-line tool for automated extraction and summarization of morphometric features from neuron morphology files (SWC format) using [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm). It supports batch processing, flexible feature selection, tag-based extraction, and outputs results in convenient CSV formats for downstream analysis. This package also supports the extraction of [ABEL](https://pubmed.ncbi.nlm.nih.gov/36196621/), a recently discovered morphometric feature. 


---

## Quick Install

**From PyPI (recommended):**
```bash
pip install morphomeasure
```

**Or for development:**
```bash
git clone https://github.com/Masood-Akram/MorphoMeasure.git
cd MorphoMeasure
pip install -e .
```


---

## Features

- **Python package & CLI for automated neuronal morphometric extraction using L-Measure** 
- **Batch processing of many SWC files** 
- **Outputs both branch-by-branch and summary morphometrics** 
- **Handles dendritic (3.0, 4.0) and glial (7.0) tags** 
- **Requires no Java or L-Measure installation - Lm.exe is bundled** 


---

## Requirements

- Python 3.9+
- [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm) (`Lm.exe`) is bundled with the package
- `pandas` (auto-installed)

---

## Usage

### Python API

```bash
from morphomeasure import LMeasureWrapper
from morphomeasure.features import features

lm = LMeasureWrapper()  # Uses bundled Lm.exe by default
df = lm.extract_features(
    swc_file='/path/to/file.swc',
    features_dict=features,
    tag='3.0',
    tmp_dir='tmp'
)

```

### As a CLI Tool

```bash
morphomeasure --tag 3.0 --features all --swc_dir /path/to/swc_files --output_dir /path/to/output
```

### All options:

```bash
morphomeasure --help
```

**Arguments:**

| Argument           | Description                                                                                  | Example                                    |
|--------------------|----------------------------------------------------------------------------------------------|--------------------------------------------|
| `--tag`            | Tags to process (e.g., 3.0 for basal, 4.0 for apical, 7.0 for glia)                         | `--tag 3.0 4.0`                            |
| `--features`       | Output type: `all`, `branch`, or `combined`                                                  | `--features all`                           |
| `--swc_dir`        | Directory containing input SWC files                                                         | `--swc_dir ./swc_files`                    |
| `--output_dir`     | Directory to save output CSVs                                                                | `--output_dir ./Measurements`              |
| `--tmp_dir`        | Temporary directory for intermediate files (default: `./tmp`)                                | `--tmp_dir ./tmp`                          |
| `--lm_exe_path`    | Path to L-Measure executable (default: bundled with package)                                 | `--lm_exe_path ./Lm/Lm.exe`                |


## Output

- **Branch-by-branch CSVs:**  
  `Measurements/<tag_label>/Branch_Morphometrics_<neuron>.csv`
- **Summary CSVs:**  
  - `All_Morphometrics.csv` (combined)
  - `All_Morphometrics_basal.csv`
  - `All_Morphometrics_apical.csv`
  - `All_Morphometrics_glia.csv`
- **Temporary files:**  
  Cleaned up automatically from the `tmp` directory.

---

## Customization

- **Features:**  
  Edit morphomeasure/features.py to add or remove L-Measure features.
- **Summary Logic:**  
  Update the summary_logic dictionary in features.py.
- **Tag Labels:**  
  Edit TAG_LABELS in features.py.

---

## Directory Structure

```
MorphoMeasure/
├── morphomeasure/
│   ├── cli.py
│   ├── features.py
│   ├── lmwrapper.py
│   └── ...
├── Lm/
│   └── Lm.exe
├── swc_files/
│   └── *.swc
├── Measurements/
│   └── Branch_Morphometrics_*.csv
├── tmp/
├── README.md
├── setup.py
└── tests/
    └── test_import.py
```

---

## Notes

- Temporary CSVs are cleaned up from tmp/ after processing.
- Make sure Lm.exe is compatible with your OS (bundled version is for Windows).
- For L-Measure feature details, see the [L-Measure documentation](http://cng.gmu.edu:8080/Lm/help/index.htm).

---

## Roadmap

- [ ] Extract features with tag 3 (basal) and tag 4 (apical) together and separately.
- [ ] Extract features with tag 7 (glia).
- [ ] PCA on Height, Width, and Depth.
- [ ] Pure Python feature extraction (no L-Measure dependency).
- [ ] Separate measures for apical & basal trees.

---

## License

MIT License

---

## Acknowledgments

- L-Measure: Center for Neural Informatics, Neural Structures, & Neural Plasticity, George Mason University

---

**For questions or contributions, please open an issue or pull request!**