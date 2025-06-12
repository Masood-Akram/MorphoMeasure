import os
import subprocess
import pandas as pd

# === Feature dictionary as you provided ===
features = {
    "Soma_Surface": "-l1,2,8,1.0 -f0,0,0,10.0",
    "N_stems": "-l1,2,8,3.0 -f1,0,0,10.0",
    "N_bifs": "-l1,2,8,3.0 -f2,0,0,10.0",
    "N_branch": "-l1,2,8,3.0 -f3,0,0,10.0",
    "N_tips": "-l1,2,8,3.0 -f4,0,0,10.0",
    "Width": "-l1,2,8,3.0 -f5,0,0,10.0",
    "Height": "-l1,2,8,3.0 -f6,0,0,10.0",
    "Depth": "-l1,2,8,3.0 -f7,0,0,10.0",
    "Diameter": "-l1,2,8,3.0 -f9,0,0,10.0",
    "Length": "-l1,2,8,3.0 -f11,0,0,10.0",
    "Surface": "-l1,2,8,3.0 -f12,0,0,10.0",
    "Volume": "-l1,2,8,3.0 -f14,0,0,10.0",
    "EucDistance": "-l1,2,8,3.0 -f15,0,0,10.0",
    "PathDistance": "-l1,2,8,3.0 -f16,0,0,10.0",
    "Branch_Order": "-l1,2,8,3.0 -f18,0,0,10.0",
    "Branch_pathlength": "-l1,2,8,3.0 -f23,0,0,10.0",
    "Contraction": "-l1,2,8,3.0 -f24,0,0,10.0",
    "Fragmentation": "-l1,2,8,3.0 -f25,0,0,10.0",
    "Partition_asymmetry": "-l1,2,8,3.0 -f28,0,0,10.0",
    "Pk_classic": "-l1,2,8,3.0 -f31,0,0,10.0",
    "Bif_ampl_local": "-l1,2,8,3.0 -f33,0,0,10.0",
    "Bif_ampl_remote": "-l1,2,8,3.0 -f34,0,0,10.0",
    "Bif_tilt_local": "-l1,2,8,3.0 -f35,0,0,10.0",
    "Bif_tilt_remote": "-l1,2,8,3.0 -f36,0,0,10.0",
    "Bif_torque_local": "-l1,2,8,3.0 -f37,0,0,10.0",
    "Bif_torque_remote": "-l1,2,8,3.0 -f38,0,0,10.0",
    "Helix": "-l1,2,8,3.0 -f43,0,0,10.0",
    "Fractal_Dim": "-l1,2,8,3.0 -f44,0,0,10.0",
    "Branch_pathlength_terminal": "-l1,2,8,3.0 -l1,2,19,1.0 -f23,0,0,10.0",
    "Contraction_terminal": "-l1,2,8,3.0 -l1,2,19,1.0 -f24,0,0,10.0",
    "Branch_pathlength_internal": "-l1,2,8,3.0 -l1,3,19,1.0 -f23,0,0,10.0",
    "Contraction_internal": "-l1,2,8,3.0 -l1,3,19,1.0 -f24,0,0,10.0"
}

# === Paths ===
swc_dir = r"C:\Users\MasoodAkram\Desktop\GitHub\MorphoMeasure\swc_files"
output_dir = r"C:\Users\MasoodAkram\Desktop\GitHub\MorphoMeasure\Measurements"
tmp_dir = r"C:\Users\MasoodAkram\Desktop\GitHub\MorphoMeasure\tmp"
lm_exe_path = r"C:\Users\MasoodAkram\Desktop\GitHub\MorphoMeasure\Lm.exe"

os.makedirs(output_dir, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

# === Utility functions for summary ===
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

# Output order (customize as needed)
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

# === MAIN PIPELINE ===
for swc_filename in os.listdir(swc_dir):
    if swc_filename.endswith(".swc"):
        swc_path = os.path.join(swc_dir, swc_filename)
        swc_base = os.path.splitext(swc_filename)[0]
        print(f"\n🧠 Processing SWC file: {swc_filename}")

        # Extract features branch-by-branch
        feature_dfs = []
        for feature_name, feature_flags in features.items():
            print(f"🔧 Feature: {feature_name}")
            temp_output_path = os.path.join(tmp_dir, f"{swc_base}_{feature_name}.csv")
            lmin_path = os.path.join(tmp_dir, "Lmin.txt")
            param_lines = f"{feature_flags}\n-s{temp_output_path} -R\n{swc_path}\n"
            with open(lmin_path, "w") as f:
                f.write(param_lines)
            result = subprocess.run([lm_exe_path, lmin_path], capture_output=True, text=True)
            if os.path.exists(temp_output_path):
                try:
                    df_raw = pd.read_csv(temp_output_path, header=None)
                    df_clean = df_raw[pd.to_numeric(df_raw[0], errors='coerce').notna()]
                    df_clean.columns = [feature_name]
                    feature_dfs.append(df_clean.reset_index(drop=True))
                    print(f"✅ Loaded {len(df_clean)} clean values")
                except Exception as e:
                    print(f"⚠️ Error reading {feature_name}: {e}")
            else:
                print(f"❌ No output for {feature_name}")

        # Save full branch-by-branch morphometrics
        if feature_dfs:
            df_combined = pd.concat(feature_dfs, axis=1)
            morpho_outfile = os.path.join(output_dir, f"Branch_Morphometrics_{swc_base}.csv")
            df_combined.to_csv(morpho_outfile, index=False)
            print(f"📁 Saved: {morpho_outfile}")

            # --- Compute summary ---
            summary = {}
            # Logic for summary features (edit to match your requirements)
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
            # Run summary logic
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
            # Sum and Max for EucDistance and PathDistance
            if "EucDistance" in df_combined.columns:
                summary["Sum_EucDistance"] = pd.to_numeric(df_combined["EucDistance"], errors="coerce").sum()
            if "PathDistance" in df_combined.columns:
                summary["Sum_PathDistance"] = pd.to_numeric(df_combined["PathDistance"], errors="coerce").sum()
            # ABEL/BAPL logic
            summary["ABEL"] = abel(df_combined, "Branch_pathlength", "Contraction")
            summary["ABEL_Terminal"] = abel(df_combined, "Branch_pathlength_terminal", "Contraction_terminal")
            summary["ABEL_internal"] = abel(df_combined, "Branch_pathlength_internal", "Contraction_internal")
            summary["BAPL"] = bapl(df_combined, "Branch_pathlength")
            summary["BAPL_Terminal"] = bapl(df_combined, "Branch_pathlength_terminal")
            summary["BAPL_Internal"] = bapl(df_combined, "Branch_pathlength_internal")

            # Output summary in order with "Features" and swc_filename column
            output_rows = []
            for feature in output_order:
                if feature in summary:
                    output_rows.append([feature, summary[feature]])
            df_output = pd.DataFrame(output_rows, columns=["Features", swc_filename])
            morpho_summary_outfile = os.path.join(output_dir, f"Morphometrics_{swc_base}.csv")
            df_output.to_csv(morpho_summary_outfile, index=False)
            print(f"📁 Saved summary: {morpho_summary_outfile}")

        else:
            print(f"⚠️ No features extracted for {swc_filename}")

# Clean up tmp folder
for fname in os.listdir(tmp_dir):
    if fname.endswith(".csv"):
        try:
            os.remove(os.path.join(tmp_dir, fname))
        except Exception as e:
            print(f"⚠️ Failed to delete {fname}: {e}")
print("\n🧹 All temporary CSVs cleaned up from tmp folder.")

