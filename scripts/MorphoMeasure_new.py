import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from morphomeasure import LMeasureWrapper
import os
import pandas as pd
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
swc_dir = os.path.join(PROJECT_ROOT, "swc_files")
output_dir = os.path.join(PROJECT_ROOT, "Measurements")
tmp_dir = os.path.join(PROJECT_ROOT, "tmp")
lm_exe_path = os.path.join(PROJECT_ROOT, "Lm.exe")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

features = {
    "Soma_Surface": "-l1,2,8,1.0 -f0,0,0,10.0",
    "N_stems": "-l1,2,8,{TAG} -f1,0,0,10.0",
    "N_bifs": "-l1,2,8,{TAG} -f2,0,0,10.0",
    "N_branch": "-l1,2,8,{TAG} -f3,0,0,10.0",
    "N_tips": "-l1,2,8,{TAG} -f4,0,0,10.0",
    "Width": "-l1,2,8,{TAG} -f5,0,0,10.0",
    "Height": "-l1,2,8,{TAG} -f6,0,0,10.0",
    "Depth": "-l1,2,8,{TAG} -f7,0,0,10.0",
    "Diameter": "-l1,2,8,{TAG} -f9,0,0,10.0",
    "Length": "-l1,2,8,{TAG} -f11,0,0,10.0",
    "Surface": "-l1,2,8,{TAG} -f12,0,0,10.0",
    "Volume": "-l1,2,8,{TAG} -f14,0,0,10.0",
    "EucDistance": "-l1,2,8,{TAG} -f15,0,0,10.0",
    "PathDistance": "-l1,2,8,{TAG} -f16,0,0,10.0",
    "Branch_Order": "-l1,2,8,{TAG} -f18,0,0,10.0",
    "Branch_pathlength": "-l1,2,8,{TAG} -f23,0,0,10.0",
    "Contraction": "-l1,2,8,{TAG} -f24,0,0,10.0",
    "Fragmentation": "-l1,2,8,{TAG} -f25,0,0,10.0",
    "Partition_asymmetry": "-l1,2,8,{TAG} -f28,0,0,10.0",
    "Pk_classic": "-l1,2,8,{TAG} -f31,0,0,10.0",
    "Bif_ampl_local": "-l1,2,8,{TAG} -f33,0,0,10.0",
    "Bif_ampl_remote": "-l1,2,8,{TAG} -f34,0,0,10.0",
    "Bif_tilt_local": "-l1,2,8,{TAG} -f35,0,0,10.0",
    "Bif_tilt_remote": "-l1,2,8,{TAG} -f36,0,0,10.0",
    "Bif_torque_local": "-l1,2,8,{TAG} -f37,0,0,10.0",
    "Bif_torque_remote": "-l1,2,8,{TAG} -f38,0,0,10.0",
    "Helix": "-l1,2,8,{TAG} -f43,0,0,10.0",
    "Fractal_Dim": "-l1,2,8,{TAG} -f44,0,0,10.0",
    "Branch_pathlength_terminal": "-l1,2,8,{TAG} -l1,2,19,1.0 -f23,0,0,10.0",
    "Contraction_terminal": "-l1,2,8,{TAG} -l1,2,19,1.0 -f24,0,0,10.0",
    "Branch_pathlength_internal": "-l1,2,8,{TAG} -l1,3,19,1.0 -f23,0,0,10.0",
    "Contraction_internal": "-l1,2,8,{TAG} -l1,3,19,1.0 -f24,0,0,10.0"
}

TAG_LABELS = {
    '3.0': 'basal_dendrites',
    '4.0': 'apical_dendrites',
    '7.0': 'glia_processes'
}

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

output_order = [
    "Soma_Surface", "N_stems", "N_bifs", "N_branch", "N_tips", "Width", "Height", "Depth",
    "Diameter", "Length", "Surface", "Volume",
    "EucDistance", "Sum_EucDistance",
    "PathDistance", "Sum_PathDistance",
    "Branch_Order", "Branch_pathlength", "Contraction", "Fragmentation",
    "Partition_asymmetry", "Pk_classic", "Bif_ampl_local", "Bif_ampl_remote",
    "Bif_tilt_local", "Bif_tilt_remote", "Bif_torque_local", "Bif_torque_remote",
    "Helix", "Fractal_Dim", "ABEL", "ABEL_Terminal", "ABEL_internal",
    "BAPL", "BAPL_Terminal", "BAPL_Internal"
]

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')

    parser = argparse.ArgumentParser(description="Extract morphometric features from SWC files using L-Measure.")
    parser.add_argument('--tag', nargs='+', required=True, help='Tags to process (e.g., 3.0 4.0)')
    parser.add_argument('--features', choices=['all', 'branch', 'combined'], default='all',
                        help='Which outputs to produce: all (summary only), branch (branch-by-branch only), combined (both)')
    args = parser.parse_args()
    tags = args.tag
    features_mode = args.features

    lm = LMeasureWrapper(lm_exe_path)

    all_summaries_combined = {}
    all_summaries = {t: {} for t in tags}

    for swc_filename in os.listdir(swc_dir):
        if not swc_filename.endswith(".swc"):
            continue
        swc_path = os.path.join(swc_dir, swc_filename)
        swc_base = os.path.splitext(swc_filename)[0]

        per_tag_dfs = {}

        # ---- Only generate branch-by-branch files if needed ----
        if features_mode in ['branch', 'combined']:
            for tag in tags:
                tag_dir = os.path.join(output_dir, TAG_LABELS.get(tag, f"tag_{tag}"))
                os.makedirs(tag_dir, exist_ok=True)
                df_tag = lm.extract_features(
                    swc_file=swc_path,
                    features_dict=features,
                    tag=tag,
                    tmp_dir=tmp_dir
                )
                morpho_outfile = os.path.join(tag_dir, f"Branch_Morphometrics_{swc_base}.csv")
                df_tag.to_csv(morpho_outfile, index=False)
                per_tag_dfs[tag] = df_tag
                # Per-tag summary (used only for All_Morphometrics.csv if needed)
                summary = {}
                logic = {
                    "Soma_Surface":        ("first",   "Soma_Surface"),
                    "N_stems":             ("sum",     "N_stems"),
                    "N_bifs":              ("sum",     "N_bifs"),
                    "N_branch":            ("sum",     "N_branch"),
                    "N_tips":              ("sum",     "N_tips"),
                    "Width":               ("sum",     "Width"),
                    "Height":              ("sum",     "Height"),
                    "Depth":               ("sum",     "Depth"),
                    "Diameter":            ("mean",    "Diameter"),
                    "Length":              ("sum",     "Length"),
                    "Surface":             ("sum",     "Surface"),
                    "Volume":              ("sum",     "Volume"),
                    "EucDistance":         ("max",     "EucDistance"),
                    "PathDistance":        ("max",     "PathDistance"),
                    "Branch_Order":        ("max",     "Branch_Order"),
                    "Branch_pathlength":   ("sum",     "Branch_pathlength"),
                    "Contraction":         ("mean",    "Contraction"),
                    "Fragmentation":       ("sum",     "Fragmentation"),
                    "Partition_asymmetry": ("mean",    "Partition_asymmetry"),
                    "Pk_classic":          ("mean",    "Pk_classic"),
                    "Bif_ampl_local":      ("mean",    "Bif_ampl_local"),
                    "Bif_ampl_remote":     ("mean",    "Bif_ampl_remote"),
                    "Bif_tilt_local":      ("mean",    "Bif_tilt_local"),
                    "Bif_tilt_remote":     ("mean",    "Bif_tilt_remote"),
                    "Bif_torque_local":    ("mean",    "Bif_torque_local"),
                    "Bif_torque_remote":   ("mean",    "Bif_torque_remote"),
                    "Helix":               ("mean",    "Helix"),
                    "Fractal_Dim":         ("mean",    "Fractal_Dim"),
                }
                for col, (op, out_label) in logic.items():
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
                all_summaries[tag][swc_filename] = summary

        # ---- For All_Morphometrics.csv summary (in 'all' or 'combined' mode) ----
        if features_mode in ['all', 'combined']:
            if features_mode == 'all':
                for tag in tags:
                    df_tag = lm.extract_features(
                        swc_file=swc_path,
                        features_dict=features,
                        tag=tag,
                        tmp_dir=tmp_dir
                    )
                    per_tag_dfs[tag] = df_tag
                    # (summary code as above)
                    summary = {}
                    logic = {
                        "Soma_Surface":        ("first",   "Soma_Surface"),
                        "N_stems":             ("sum",     "N_stems"),
                        "N_bifs":              ("sum",     "N_bifs"),
                        "N_branch":            ("sum",     "N_branch"),
                        "N_tips":              ("sum",     "N_tips"),
                        "Width":               ("sum",     "Width"),
                        "Height":              ("sum",     "Height"),
                        "Depth":               ("sum",     "Depth"),
                        "Diameter":            ("mean",    "Diameter"),
                        "Length":              ("sum",     "Length"),
                        "Surface":             ("sum",     "Surface"),
                        "Volume":              ("sum",     "Volume"),
                        "EucDistance":         ("max",     "EucDistance"),
                        "PathDistance":        ("max",     "PathDistance"),
                        "Branch_Order":        ("max",     "Branch_Order"),
                        "Branch_pathlength":   ("sum",     "Branch_pathlength"),
                        "Contraction":         ("mean",    "Contraction"),
                        "Fragmentation":       ("sum",     "Fragmentation"),
                        "Partition_asymmetry": ("mean",    "Partition_asymmetry"),
                        "Pk_classic":          ("mean",    "Pk_classic"),
                        "Bif_ampl_local":      ("mean",    "Bif_ampl_local"),
                        "Bif_ampl_remote":     ("mean",    "Bif_ampl_remote"),
                        "Bif_tilt_local":      ("mean",    "Bif_tilt_local"),
                        "Bif_tilt_remote":     ("mean",    "Bif_tilt_remote"),
                        "Bif_torque_local":    ("mean",    "Bif_torque_local"),
                        "Bif_torque_remote":   ("mean",    "Bif_torque_remote"),
                        "Helix":               ("mean",    "Helix"),
                        "Fractal_Dim":         ("mean",    "Fractal_Dim"),
                    }
                    for col, (op, out_label) in logic.items():
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
                    all_summaries[tag][swc_filename] = summary
            if per_tag_dfs:
                df_combined = pd.concat(list(per_tag_dfs.values()), axis=0, ignore_index=True)
                summary = {}
                logic = {
                    "Soma_Surface":        ("first",   "Soma_Surface"),
                    "N_stems":             ("sum",     "N_stems"),
                    "N_bifs":              ("sum",     "N_bifs"),
                    "N_branch":            ("sum",     "N_branch"),
                    "N_tips":              ("sum",     "N_tips"),
                    "Width":               ("sum",     "Width"),
                    "Height":              ("sum",     "Height"),
                    "Depth":               ("sum",     "Depth"),
                    "Diameter":            ("mean",    "Diameter"),
                    "Length":              ("sum",     "Length"),
                    "Surface":             ("sum",     "Surface"),
                    "Volume":              ("sum",     "Volume"),
                    "EucDistance":         ("max",     "EucDistance"),
                    "PathDistance":        ("max",     "PathDistance"),
                    "Branch_Order":        ("max",     "Branch_Order"),
                    "Branch_pathlength":   ("sum",     "Branch_pathlength"),
                    "Contraction":         ("mean",    "Contraction"),
                    "Fragmentation":       ("sum",     "Fragmentation"),
                    "Partition_asymmetry": ("mean",    "Partition_asymmetry"),
                    "Pk_classic":          ("mean",    "Pk_classic"),
                    "Bif_ampl_local":      ("mean",    "Bif_ampl_local"),
                    "Bif_ampl_remote":     ("mean",    "Bif_ampl_remote"),
                    "Bif_tilt_local":      ("mean",    "Bif_tilt_local"),
                    "Bif_tilt_remote":     ("mean",    "Bif_tilt_remote"),
                    "Bif_torque_local":    ("mean",    "Bif_torque_local"),
                    "Bif_torque_remote":   ("mean",    "Bif_torque_remote"),
                    "Helix":               ("mean",    "Helix"),
                    "Fractal_Dim":         ("mean",    "Fractal_Dim"),
                }
                for col, (op, out_label) in logic.items():
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
                all_summaries_combined[swc_filename] = summary

    # ---- Build and save the All_Morphometrics.csv ----
    if features_mode in ['all', 'combined'] and all_summaries_combined:
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
            result_frames_combined = []
            for neuron in neuron_names:
                comb = all_summaries_combined[neuron]
                df = pd.DataFrame({"combined": comb})
                df.insert(0, "Features", df.index)
                df.reset_index(drop=True, inplace=True)
                result_frames_combined.append((df, neuron))
            df_out_combined = build_df_out(result_frames_combined, lambda df, n: f"{n.replace('.swc','')}_combined")
            df_out_combined.to_csv(os.path.join(output_dir, "All_Morphometrics.csv"), index=False)

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

    # Clean up tmp folder
    for fname in os.listdir(tmp_dir):
        if fname.endswith(".csv"):
            try:
                os.remove(os.path.join(tmp_dir, fname))
            except Exception:
                pass
