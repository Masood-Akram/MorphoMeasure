import os
import subprocess
import pandas as pd
import tempfile
from .features import features, TAG_LABELS, output_order, summary_logic

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LM_EXE = os.path.join(PACKAGE_ROOT, "..", "Lm", "Lm.exe")

def abel(df, path_col, contract_col):
    if path_col in df.columns and contract_col in df.columns:
        p = pd.to_numeric(df[path_col], errors="coerce")
        c = pd.to_numeric(df[contract_col], errors="coerce")
        return (p * c).mean()
    return None

def bapl(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").mean()
    return None

class LMeasureWrapper:
    def __init__(self, lm_exe_path=None):
        if lm_exe_path is None:
            package_root = os.path.dirname(os.path.abspath(__file__))
            self.lm_exe_path = os.path.join(package_root, "..", "Lm", "Lm.exe")
        else:
            self.lm_exe_path = lm_exe_path

    def extract_features(self, swc_file, features_dict, tag):
        feature_arrays = {}
        max_len = 0
        with tempfile.TemporaryDirectory() as workdir:
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

    def run_batch(self, swc_dir, output_dir, tags, features_mode=('all',), features_dict=features, summary_logic=summary_logic):
        # Accepts list/tuple/str for features_mode
        if isinstance(features_mode, str):
            features_mode_set = {features_mode}
        else:
            features_mode_set = set(features_mode)

        os.makedirs(output_dir, exist_ok=True)
        all_summaries_combined = {}
        all_summaries = {t: {} for t in tags}

        for swc_file in os.listdir(swc_dir):
            if not swc_file.endswith('.swc'):
                continue
            swc_path = os.path.join(swc_dir, swc_file)
            swc_base = os.path.splitext(swc_file)[0]
            per_tag_dfs = {}

            # Branch-by-branch morphometrics
            if 'branch' in features_mode_set or 'combined' in features_mode_set:
                for tag in tags:
                    tag_dir = os.path.join(output_dir, TAG_LABELS.get(tag, f"tag_{tag}"))
                    os.makedirs(tag_dir, exist_ok=True)
                    df_tag = self.extract_features(swc_file=swc_path, features_dict=features_dict, tag=tag)
                    morpho_outfile = os.path.join(tag_dir, f"Branch_Morphometrics_{swc_base}.csv")
                    df_tag.to_csv(morpho_outfile, index=False)
                    per_tag_dfs[tag] = df_tag
                    # Also do summary for each tag
                    summary = {}
                    for col, (op, out_label) in summary_logic.items():
                        if col in df_tag.columns:
                            col_numeric = pd.to_numeric(df_tag[col], errors="coerce")
                            if op == "sum":
                                summary[out_label] = col_numeric.sum()
                            elif op == "mean":
                                summary[out_label] = col_numeric.mean()
                            elif op == "max":
                                summary[out_label] = col_numeric.max()
                            elif op == "first":
                                summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                    if "EucDistance" in df_tag.columns:
                        summary["Sum_EucDistance"] = pd.to_numeric(df_tag["EucDistance"], errors="coerce").sum()
                    if "PathDistance" in df_tag.columns:
                        summary["Sum_PathDistance"] = pd.to_numeric(df_tag["PathDistance"], errors="coerce").sum()
                    summary["ABEL"] = abel(df_tag, "Branch_pathlength", "Contraction")
                    summary["ABEL_Terminal"] = abel(df_tag, "Branch_pathlength_terminal", "Contraction_terminal")
                    summary["ABEL_internal"] = abel(df_tag, "Branch_pathlength_internal", "Contraction_internal")
                    summary["BAPL"] = bapl(df_tag, "Branch_pathlength")
                    summary["BAPL_Terminal"] = bapl(df_tag, "Branch_pathlength_terminal")
                    summary["BAPL_Internal"] = bapl(df_tag, "Branch_pathlength_internal")
                    all_summaries[tag][swc_file] = summary

            # For All_Morphometrics summary (if 'all' or 'combined')
            if 'all' in features_mode_set or 'combined' in features_mode_set:
                if 'all' in features_mode_set:
                    for tag in tags:
                        df_tag = self.extract_features(swc_file=swc_path, features_dict=features_dict, tag=tag)
                        per_tag_dfs[tag] = df_tag
                        summary = {}
                        for col, (op, out_label) in summary_logic.items():
                            if col in df_tag.columns:
                                col_numeric = pd.to_numeric(df_tag[col], errors="coerce")
                                if op == "sum":
                                    summary[out_label] = col_numeric.sum()
                                elif op == "mean":
                                    summary[out_label] = col_numeric.mean()
                                elif op == "max":
                                    summary[out_label] = col_numeric.max()
                                elif op == "first":
                                    summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                        if "EucDistance" in df_tag.columns:
                            summary["Sum_EucDistance"] = pd.to_numeric(df_tag["EucDistance"], errors="coerce").sum()
                        if "PathDistance" in df_tag.columns:
                            summary["Sum_PathDistance"] = pd.to_numeric(df_tag["PathDistance"], errors="coerce").sum()
                        summary["ABEL"] = abel(df_tag, "Branch_pathlength", "Contraction")
                        summary["ABEL_Terminal"] = abel(df_tag, "Branch_pathlength_terminal", "Contraction_terminal")
                        summary["ABEL_internal"] = abel(df_tag, "Branch_pathlength_internal", "Contraction_internal")
                        summary["BAPL"] = bapl(df_tag, "Branch_pathlength")
                        summary["BAPL_Terminal"] = bapl(df_tag, "Branch_pathlength_terminal")
                        summary["BAPL_Internal"] = bapl(df_tag, "Branch_pathlength_internal")
                        all_summaries[tag][swc_file] = summary
                if per_tag_dfs:
                    df_combined = pd.concat(list(per_tag_dfs.values()), axis=0, ignore_index=True)
                    summary = {}
                    for col, (op, out_label) in summary_logic.items():
                        if col in df_combined.columns:
                            col_numeric = pd.to_numeric(df_combined[col], errors="coerce")
                            if op == "sum":
                                summary[out_label] = col_numeric.sum()
                            elif op == "mean":
                                summary[out_label] = col_numeric.mean()
                            elif op == "max":
                                summary[out_label] = col_numeric.max()
                            elif op == "first":
                                summary[out_label] = col_numeric.iloc[0] if not col_numeric.empty else None
                    if "EucDistance" in df_combined.columns:
                        summary["Sum_EucDistance"] = pd.to_numeric(df_combined["EucDistance"], errors="coerce").sum()
                    if "PathDistance" in df_combined.columns:
                        summary["Sum_PathDistance"] = pd.to_numeric(df_combined["PathDistance"], errors="coerce").sum()
                    summary["ABEL"] = abel(df_combined, "Branch_pathlength", "Contraction")
                    summary["ABEL_Terminal"] = abel(df_combined, "Branch_pathlength_terminal", "Contraction_terminal")
                    summary["ABEL_internal"] = abel(df_combined, "Branch_pathlength_internal", "Contraction_internal")
                    summary["BAPL"] = bapl(df_combined, "Branch_pathlength")
                    summary["BAPL_Terminal"] = bapl(df_combined, "Branch_pathlength_terminal")
                    summary["BAPL_Internal"] = bapl(df_combined, "Branch_pathlength_internal")
                    all_summaries_combined[swc_file] = summary

        # ---- End per-file loop

        # --- After all files processed, write All_Morphometrics summaries ---
        if ('all' in features_mode_set or 'combined' in features_mode_set) and all_summaries_combined:
            neuron_names = sorted(all_summaries_combined.keys())
            all_features = output_order

            def build_df_out(result_frames, column_name_func):
                df_out = pd.DataFrame({"Features": all_features})
                for df, neuron in result_frames:
                    colname = column_name_func(df, neuron)
                    df1 = df.set_index("Features")[df.columns[1]]
                    df_out[colname] = df1.reindex(all_features).values
                return df_out

            only_glia = (len(tags) == 1 and tags[0] == "7.0")
            contains_glia = "7.0" in tags

            if set(tags) == {"3.0", "4.0"} and not contains_glia:
                # Combined CSV
                result_frames_combined = []
                for neuron in neuron_names:
                    comb = all_summaries_combined[neuron]
                    df = pd.DataFrame({"combined": comb})
                    df.insert(0, "Features", df.index)
                    df.reset_index(drop=True, inplace=True)
                    result_frames_combined.append((df, neuron))
                df_out_combined = build_df_out(result_frames_combined, lambda df, n: f"{n.replace('.swc','')}_combined")
                df_out_combined.to_csv(os.path.join(output_dir, "All_Morphometrics.csv"), index=False)

                # Basal
                result_frames_basal = []
                for neuron in neuron_names:
                    tag_label = TAG_LABELS["3.0"]
                    val = all_summaries["3.0"].get(neuron, {})
                    df = pd.DataFrame({tag_label: val})
                    df.insert(0, "Features", df.index)
                    df.reset_index(drop=True, inplace=True)
                    result_frames_basal.append((df, neuron))
                df_out_basal = build_df_out(result_frames_basal, lambda df, n: f"{n.replace('.swc','')}_basal_dendrites")
                df_out_basal.to_csv(os.path.join(output_dir, "All_Morphometrics_basal.csv"), index=False)

                # Apical
                result_frames_apical = []
                for neuron in neuron_names:
                    tag_label = TAG_LABELS["4.0"]
                    val = all_summaries["4.0"].get(neuron, {})
                    df = pd.DataFrame({tag_label: val})
                    df.insert(0, "Features", df.index)
                    df.reset_index(drop=True, inplace=True)
                    result_frames_apical.append((df, neuron))
                df_out_apical = build_df_out(result_frames_apical, lambda df, n: f"{n.replace('.swc','')}_apical_dendrites")
                df_out_apical.to_csv(os.path.join(output_dir, "All_Morphometrics_apical.csv"), index=False)

            else:
                for tag in tags:
                    tag_label = TAG_LABELS.get(tag, f"tag_{tag}")
                    result_frames = []
                    for neuron in neuron_names:
                        val = all_summaries[tag].get(neuron, {})
                        df = pd.DataFrame({tag_label: val})
                        df.insert(0, "Features", df.index)
                        df.reset_index(drop=True, inplace=True)
                        result_frames.append((df, neuron))
                    if tag == "3.0":
                        outname = "All_Morphometrics_basal.csv"
                    elif tag == "4.0":
                        outname = "All_Morphometrics_apical.csv"
                    elif tag == "7.0":
                        outname = "All_Morphometrics_glia.csv"
                    else:
                        outname = f"All_Morphometrics_{tag_label}.csv"
                    df_out = build_df_out(result_frames, lambda df, n: f"{n.replace('.swc','')}_{tag_label}")
                    df_out.to_csv(os.path.join(output_dir, outname), index=False)
