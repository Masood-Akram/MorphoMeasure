import os
import subprocess
import pandas as pd
import tempfile

class LMeasureWrapper:
    def __init__(self, lm_exe_path):
        self.lm_exe_path = lm_exe_path

    def extract_features(self, swc_file, features_dict, tag, tmp_dir):
        feature_arrays = {}
        max_len = 0

        with tempfile.TemporaryDirectory(dir=tmp_dir) as workdir:
            for feature_name, feature_flag in features_dict.items():
                feature_flag = feature_flag.replace('{TAG}', tag)
                lmin_path = os.path.join(workdir, 'Lmin.txt')
                out_path = os.path.join(workdir, f'{feature_name}.csv')
                param = f"{feature_flag}\n-s{out_path} -R\n{swc_file}\n"
                with open(lmin_path, "w") as f:
                    f.write(param)
                subprocess.run([self.lm_exe_path, lmin_path], capture_output=True, text=True)
                if os.path.exists(out_path):
                    try:
                        df = pd.read_csv(out_path, header=None)
                        arr = df[pd.to_numeric(df[0], errors='coerce').notna()][0].tolist()
                    except Exception:
                        arr = [None]
                else:
                    arr = [None]
                feature_arrays[feature_name] = arr
                if len(arr) > max_len:
                    max_len = len(arr)

        # Pad all arrays to the same length
        for key in feature_arrays:
            arr = feature_arrays[key]
            if len(arr) < max_len:
                arr = arr + [None] * (max_len - len(arr))
            feature_arrays[key] = arr

        return pd.DataFrame(feature_arrays)