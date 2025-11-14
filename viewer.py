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
        import os
        from pathlib import Path
        import streamlit as st
        import pandas as pd
        from pandas.errors import ParserError
        import streamlit.components.v1 as components


        def find_data_path() -> Path:
            """Return project data/crypto_data.csv if present, else fallback to venv/data."""
            base = Path(__file__).parent
            p = base / "data" / "crypto_data.csv"
            if p.exists():
                return p
            v = base / "venv" / "data" / "crypto_data.csv"
            return v if v.exists() else None


        def safe_read_csv(path: Path) -> pd.DataFrame:
            """Read CSV robustly: try fast parser, then fallback to python engine skipping bad lines."""
            try:
                return pd.read_csv(path)
            except ParserError:
                # fall back and skip malformed lines
                return pd.read_csv(path, engine="python", on_bad_lines="skip")


        def main():
            st.set_page_config(page_title="Crypto CSV Viewer", layout="wide")
            st.title("Crypto CSV Viewer")

            data_path = find_data_path()
            if data_path is None:
                st.info("No `data/crypto_data.csv` found. Upload a CSV below.")
                uploaded = st.file_uploader("Upload CSV", type=["csv"])
                if not uploaded:
                    st.stop()
                try:
                    df = pd.read_csv(uploaded)
                except ParserError:
                    st.warning("Uploaded CSV is malformed; attempting to read while skipping bad lines.")
                    df = pd.read_csv(uploaded, engine="python", on_bad_lines="skip")
                except Exception as e:
                    st.error(f"Failed to read uploaded CSV: {e}")
                    st.stop()
            else:
                try:
                    df = safe_read_csv(data_path)
                    st.success(f"Loaded: {data_path}")
                except Exception as e:
                    st.error(f"Failed to read {data_path}: {e}")
                    st.stop()

            st.subheader("Data")
            st.dataframe(df)

            # Download current CSV
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
                        if (b.innerText && b.innerText.includes('Close (Press Enter)')) { b.click(); break; }
                    }
                }
            });
            </script>
            """

            components.html(js, height=0)


        if __name__ == '__main__':
            main()
    st.markdown("---")
