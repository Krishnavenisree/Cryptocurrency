import os
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def find_data_path() -> Path:
    """Look for data/crypto_data.csv in repo root first, then fallback to venv/data."""
    base = Path(__file__).parent
    project_path = base / "data" / "crypto_data.csv"
    if project_path.exists():
        return project_path
    venv_path = base / "venv" / "data" / "crypto_data.csv"
    if venv_path.exists():
        # copy to project data location for future runs
        target_dir = base / "data"
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            import shutil

            shutil.copy2(venv_path, project_path)
            return project_path
        except Exception:
            return venv_path
    return None


def main():
    st.set_page_config(page_title="Crypto CSV Viewer", layout="wide")
    st.title("Crypto CSV Viewer")

    data_path = find_data_path()
    if data_path is None:
        st.info("Could not find `venv/data/crypto_data.csv`. You can upload a CSV below.")
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded is None:
            st.stop()
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
            st.stop()
    else:
        try:
            df = pd.read_csv(data_path)
            st.success(f"Loaded: {data_path}")
        except Exception as e:
            st.error(f"Failed to read {data_path}: {e}")
            st.stop()

    st.subheader("Data")
    st.dataframe(df)

    # --- Compare with previous snapshot and show deltas ---
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    prev_path = data_dir / "prev_crypto_snapshot.csv"

    def choose_key_column(df: pd.DataFrame):
        for candidate in ("coin", "name", "symbol", "id"):
            if candidate in df.columns:
                return candidate
        return None

    if prev_path.exists():
        try:
            prev_df = pd.read_csv(prev_path)
        except Exception as e:
            st.warning(f"Could not read previous snapshot: {e}")
            prev_df = None
    else:
        prev_df = None

    if prev_df is not None:
        # attempt to align rows using a key column if present, else use index alignment
        key = choose_key_column(df)
        if key and key in prev_df.columns:
            cur = df.set_index(key)
            pr = prev_df.set_index(key)
        else:
            # align by index positions; if prev has different shape, we'll compare overlapping rows
            cur = df.copy()
            pr = prev_df.copy()

        # determine numeric columns present in both
        num_cols = [c for c in cur.select_dtypes(include=["number"]).columns if c in pr.columns]
        if not num_cols:
            st.info("No numeric columns available to compute changes since last run.")
        else:
            primary = num_cols[0]
            # align indices
            common_index = cur.index.intersection(pr.index)
            if common_index.empty:
                st.info("No overlapping rows between current data and previous snapshot to compare.")
            else:
                cur_vals = cur.loc[common_index, primary].astype(float)
                prev_vals = pr.loc[common_index, primary].astype(float)
                delta = cur_vals - prev_vals
                direction = delta.apply(lambda x: "up" if x > 0 else ("down" if x < 0 else "no change"))
                summary = pd.DataFrame({
                    "key": common_index,
                    f"prev_{primary}": prev_vals.values,
                    f"cur_{primary}": cur_vals.values,
                    "delta": delta.values,
                    "direction": direction.values,
                })
                summary = summary.reset_index(drop=True)
                st.subheader(f"Changes since last run (by {primary})")
                st.dataframe(summary)
    else:
        st.info("No previous snapshot found — this run will be saved and used for future comparisons.")

    # save current snapshot for next run
    try:
        df.to_csv(prev_path, index=False)
    except Exception as e:
        st.warning(f"Could not save snapshot for next run: {e}")

    try:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv_bytes, file_name=(data_path.name if data_path else "crypto_data.csv"), mime="text/csv", key="download_csv")
    except Exception as e:
        st.error(f"Could not prepare CSV for download: {e}")

    st.markdown("---")

    if st.button("Close (Press Enter)"):
        try:
            os._exit(0)
        except Exception:
            pass

    js = r"""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            try { window.close(); } catch (err) { }
            const buttons = Array.from(document.querySelectorAll('button'));
            for (const b of buttons) {
                if (b.innerText && b.innerText.includes('Close (Press Enter)')) {
                    b.click();
                    break;
                }
            }
        }
    });
    </script>
    """

    components.html(js, height=0)


if __name__ == '__main__':
    main()
