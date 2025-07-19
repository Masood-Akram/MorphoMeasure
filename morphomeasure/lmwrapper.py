import os
import subprocess
import pandas as pd
import tempfile

class LMeasureWrapper:
    def __init__(self, lm_exe_path):
        self.lm_exe_path = lm_exe_path

    def extract_features(self, swc_file, features_dict, tag, tmp_dir):
        """
        Run L-Measure for the given SWC file and tag.
        Returns: a pandas DataFrame of features (columns) and values.
        """
        results = {}
        for feature_name, feature_flag in features_dict.items():
            feature_flag = feature_flag.replace('{TAG}', tag)
            with tempfile.TemporaryDirectory(dir=tmp_dir) as workdir:
                lmin_path = os.path.join(workdir, 'Lmin.txt')
                out_path = os.path.join(workdir, f'{feature_name}.csv')
                param = f"{feature_flag}\n-s{out_path} -R\n{swc_file}\n"
                with open(lmin_path, "w") as f:
                    f.write(param)
                subprocess.run([self.lm_exe_path, lmin_path], capture_output=True, text=True)
                if os.path.exists(out_path):
                    df = pd.read_csv(out_path, header=None)
                    df_clean = df[pd.to_numeric(df[0], errors='coerce').notna()]
                    results[feature_name] = df_clean[0].values
                else:
                    results[feature_name] = [None]
        return pd.DataFrame(results)
