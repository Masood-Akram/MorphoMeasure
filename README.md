# MorphoMeasure

Python Package & CLI Wrapper for L-Measure

![CI](https://github.com/Masood-Akram/MorphoMeasure/actions/workflows/python-package.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/morphomeasure.svg)](https://pypi.org/project/morphomeasure/)
[![PyPI version](https://img.shields.io/pypi/v/morphomeasure.svg)](https://pypi.org/project/morphomeasure/)


*MorphoMeasure* is a Python package and command-line tool for automated extraction and summarization of morphometric features from neuron morphology files (SWC format) using [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm). It supports batch processing, flexible feature selection, tag-based extraction, and outputs results in convenient CSV formats for downstream analysis.


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
- **Requires no Java or L-Measure installation—Lm.exe is bundled** 



Cross-platform (tested: Windows, Linux, Mac)



---

## Requirements

- Python 3.9+
- [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm) (`Lm.exe`) placed in the `Lm` directory or specify its path
- `pandas` (`pip install pandas`)

---

## Installation

1. **Clone this repository:**
   ```sh
   git clone https://github.com/Masood-Akram/MorphoMeasure.git
   cd MorphoMeasure
   ```

2. **Install dependencies:**
   ```sh
   pip install pandas
   ```

3. **Place L-Measure executable:**
   - Download `Lm.exe` from the [L-Measure website](http://cng.gmu.edu:8080/Lm/help/index.htm).
   - Place it in the `Lm` directory (default), or specify its path with `--lm_exe_path`.

---

## Usage

### As a CLI Tool

```sh
python -m morphomeasure.cli \
    --tag 3.0 4.0 \
    --features combined \
    --swc_dir ./swc_files \
    --output_dir ./Measurements \
    --tmp_dir ./tmp
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

### As a Python Package

```python
from morphomeasure import LMeasureWrapper
lm = LMeasureWrapper()
df = lm.extract_features(
    swc_file='/path/to/file.swc',
    features_dict=features,      # import from morphomeasure.features
    tag='3.0',
    tmp_dir='tmp'
)

```

---

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
  Edit `features` in `morphomeasure/features.py` to add/remove L-Measure features.
- **Summary Logic:**  
  Edit `summary_logic` in `morphomeasure/features.py` to change how features are summarized (sum, mean, max, etc.).
- **Tag Labels:**  
  Update `TAG_LABELS` in `morphomeasure/features.py` for custom tag names.

---

## Directory Structure

```
MorphoMeasure/
├── morphomeasure/
│   ├── cli.py
│   ├── features.py
│   └── ...
├── Lm/
│   └── Lm.exe
├── swc_files/
│   └── *.swc
├── Measurements/
│   └── Branch_Morphometrics_*.csv
├── tmp/
├── README.md
└── setup.py
```

---

## Notes

- The script creates and cleans up temporary files in the `tmp` directory.
- Make sure `Lm.exe` is compatible with your system and accessible at the specified path.
- For more information on L-Measure feature codes and options, see the [L-Measure documentation](http://cng.gmu.edu:8080/Lm/help/index.htm).

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