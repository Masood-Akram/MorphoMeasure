import argparse
from .lmwrapper import LMeasureWrapper

def main():
    parser = argparse.ArgumentParser(description="MorphoMeasure CLI")
    parser.add_argument('--tag', nargs='+', required=True, help='Tags to process (e.g., 3.0 4.0 7.0)')
    parser.add_argument('--features', choices=['all', 'branch', 'combined'], default='all',
                        help='Which outputs to produce: all, branch, or combined')
    parser.add_argument('--swc_dir', default='swc_files', help='Directory with SWC files')
    parser.add_argument('--output_dir', default='Measurements', help='Output directory')
    parser.add_argument('--tmp_dir', default='tmp', help='Temporary directory')
    parser.add_argument('--lm_exe_path', default='Lm/Lm.exe', help='Path to L-Measure executable')
    args = parser.parse_args()

    lm = LMeasureWrapper(args.lm_exe_path)
    # Call your extraction workflow using args, similar to your script

if __name__ == "__main__":
    main()
