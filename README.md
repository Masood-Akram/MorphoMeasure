# THIS PROJECT WILL BECOME A PYTHON PACKAGE

# MorphoMeasure: Automated Morphometric Feature Extraction

This repository provides a Python workflow for automated extraction of morphometric features from neuron morphology files (SWC format) using [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm) (`Lm.exe`). The script processes multiple SWC files, extracts a comprehensive set of features, and saves the results as CSV files for downstream analysis.

## Features

- **Batch processing** of SWC files
- Extraction of a wide range of morphometric features, including:
  - Soma surface
  - Number of stems, bifurcations, branches, tips
  - Width, height, depth, diameter, length, surface, volume
  - Euclidean and path distances
  - Branch order, terminal degree
  - Branch pathlength and contraction (including for terminal and internal branches)
  - Fragmentation, partition asymmetry, bifurcation angles, and more
- **Temporary file management** for clean workspace
- **Customizable feature set** via the `features` dictionary

## Requirements

- Python 3.x
- [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm) (`Lm.exe`) placed in the repository directory
- `pandas` library

## Usage

1. **Place your SWC files** in the `swc_files` directory.
2. **Configure paths** in the script if your directory structure is different.
3. **Run the script** (e.g., in Jupyter Notebook or as a Python script):

   ```python
   # In Jupyter Notebook, run all cells
   # Or from command line:
   python morphometric_extraction.ipynb
   ```

4. **Results** will be saved in the `Measurements` directory, one CSV per SWC file.

## Directory Structure

```
MorphoMeasure/
├── morphometric_extraction.ipynb
├── Lm.exe
├── swc_files/
│   └── *.swc
├── Measurements/
│   └── Branch_Morphometrics_*.csv
├── tmp/
```

## Customizing Features

Edit the `features` dictionary in the script to add, remove, or modify the features you want to extract. Each key is a feature name, and each value is the corresponding L-Measure command-line flags.

## Notes

- The script creates and cleans up temporary files in the `tmp` directory.
- Make sure `Lm.exe` is compatible with your system and accessible at the specified path.
- For more information on L-Measure feature codes and options, see the [L-Measure documentation](http://cng.gmu.edu:8080/Lm/help/index.htm).

## License

This project is provided under the MIT License.

---