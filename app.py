import os
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def find_data_path() -> Path:
    """Return the expected local CSV path if it exists."""
    p = Path(__file__).parent / "venv" / "data" / "crypto_data.csv"
    return p if p.exists() else None


def main():
    st.set_page_config(page_title="Crypto CSV Viewer", layout="wide")
    import os
    from pathlib import Path
    import streamlit as st
    import pandas as pd
    import streamlit.components.v1 as components


    def find_data_path() -> Path:
        """Return the expected local CSV path if it exists."""
        p = Path(__file__).parent / "venv" / "data" / "crypto_data.csv"
        return p if p.exists() else None


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

        # Single download button with explicit unique key to avoid Streamlit duplicate-id errors
        try:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv_bytes, file_name=(data_path.name if data_path else "crypto_data.csv"), mime="text/csv", key="download_csv")
        except Exception as e:
            st.error(f"Could not prepare CSV for download: {e}")

        st.markdown("---")

        # Close button and JS to listen for Enter key
        if st.button("Close (Press Enter)"):
            # Best-effort server shutdown
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
