import json
import tempfile
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from engine.analyzer import analyze_github_repo, analyzer
from reports.json_report import generate_json_report

SUPPORTED_EXTENSIONS = ["py", "cpp", "cc", "cxx", "java", "js"]
DISPLAY_FILE_LIMIT = 50

st.set_page_config(page_title="Static Analyzer", page_icon="U0001F6F0", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        :root {
            --bg-a: #070b18;
            --bg-b: #121a35;
            --glass: rgba(16, 24, 52, 0.62);
            --line: rgba(148, 163, 184, 0.24);
            --text: #e2e8f0;
            --muted: #93a3c9;
            --accent: #2dd4bf;
            --accent-2: #fb7185;
        }

        html, body, [class*="css"] {
            font-family: 'Sora', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 10%, rgba(45, 212, 191, 0.20), transparent 34%),
                radial-gradient(circle at 90% 14%, rgba(251, 113, 133, 0.18), transparent 36%),
                linear-gradient(150deg, var(--bg-a), var(--bg-b));
            color: var(--text);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2.2rem;
            max-width: 1180px;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        .hero-shell {
            background: linear-gradient(130deg, rgba(45,212,191,0.14), rgba(99,102,241,0.06) 42%, rgba(251,113,133,0.14));
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1.2rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 22px 44px rgba(2, 6, 23, 0.4);
            animation: rise-in .45s ease-out;
        }

        .hero-eyebrow {
            color: #67e8f9;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            font-size: 0.72rem;
        }

        .hero-title {
            font-size: clamp(1.8rem, 3.2vw, 2.6rem);
            margin: 0.25rem 0 0.3rem;
            color: #f8fafc;
            font-weight: 800;
            line-height: 1.1;
        }

        .hero-sub {
            margin: 0;
            color: var(--muted);
            font-size: 0.95rem;
        }

        .glass-panel {
            background: var(--glass);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.9rem;
            animation: rise-in .45s ease-out;
        }

        .kpi-card {
            background: linear-gradient(170deg, rgba(15,23,42,0.68), rgba(15,23,42,0.25));
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.9rem;
            min-height: 96px;
        }

        .kpi-label {
            font-size: .72rem;
            letter-spacing: .06em;
            text-transform: uppercase;
            color: #9fb0d7;
            margin-bottom: .35rem;
            font-weight: 700;
        }

        .kpi-value {
            font-size: 1.5rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.1;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
            background: rgba(2,6,23,.35);
            border-radius: 10px;
            padding: 0.25rem;
            border: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #bfcae8;
            font-weight: 700;
            letter-spacing: .01em;
            min-height: 40px;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(130deg, rgba(45,212,191,0.22), rgba(251,113,133,0.20));
            color: #f8fafc !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(2, 6, 23, 0.60);
            border: 1px dashed rgba(96, 165, 250, 0.42);
            border-radius: 14px;
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid rgba(45,212,191,.52);
            background: linear-gradient(130deg, rgba(45,212,191,.24), rgba(56,189,248,.22));
            color: #e2e8f0;
            font-weight: 700;
            height: 2.7rem;
        }

        .stDownloadButton > button {
            border-radius: 10px;
            border: 1px solid rgba(248,250,252,.24);
            background: rgba(15,23,42,0.45);
            color: #e2e8f0;
            font-weight: 600;
        }

        [data-baseweb="radio"] {
            background: rgba(2, 6, 23, 0.42);
            border: 1px solid var(--line);
            padding: 0.35rem;
            border-radius: 12px;
        }

        [data-testid="stAlert"] {
            border-radius: 12px;
            border: 1px solid var(--line);
            background: rgba(15, 23, 42, 0.62);
        }

        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--line);
        }

        code, .stCode, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        @keyframes rise-in {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 900px) {
            .main .block-container { padding-top: 1.3rem; }
            .hero-shell { padding: 1rem; border-radius: 16px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def results_to_dataframe(results: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for result in results:
        if result.get("error"):
            continue

        metrics = result.get("metrics", {})
        rows.append(
            {
                "file": result.get("file", "unknown"),
                "language": result.get("language", "unknown"),
                "cyclomatic_max": metrics.get("cyclomatic_complexity", {}).get("max", 0),
                "cyclomatic_avg": metrics.get("cyclomatic_complexity", {}).get("average", 0),
                "halstead_volume": metrics.get("halstead", {}).get("volume", 0),
                "halstead_difficulty": metrics.get("halstead", {}).get("difficulty", 0),
                "halstead_effort": metrics.get("halstead", {}).get("effort", 0),
                "halstead_bugs": metrics.get("halstead", {}).get("estimated_bugs", 0),
                "classes": metrics.get("oop_metrics", {}).get("number_of_classes", 0),
                "methods": metrics.get("oop_metrics", {}).get("number_of_methods", 0),
                "attributes": metrics.get("oop_metrics", {}).get("number_of_attributes", 0),
                "inheritance": metrics.get("oop_metrics", {}).get("inheritance_relationships", 0),
                "method_attribute_ratio": metrics.get("oop_metrics", {}).get("method_to_attribute_ratio", 0),
            }
        )

    return pd.DataFrame(rows)


def run_uploaded_file_analysis(uploaded_files) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for uploaded in uploaded_files:
        suffix = Path(uploaded.name).suffix or ".txt"
        with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp.flush()
            result = analyzer(tmp.name)

        if result:
            result["file"] = uploaded.name
            results.append(result)

    return results


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-eyebrow"></div>
            <h1 class="hero-title">StaticLens</h1>
            <p class="hero-sub">A multi-language static code analysis tool for evaluating complexity and structural quality across repositories.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charts(frame: pd.DataFrame) -> None:
    left, right = st.columns(2)
    ranked = frame.sort_values("cyclomatic_avg", ascending=False).reset_index(drop=True).copy()
    ranked["rank"] = ranked.index + 1

    with left:
        st.markdown("<div class='glass-panel'><b>Cyclomatic Trend (Top 50)</b></div>", unsafe_allow_html=True)
        line = (
            alt.Chart(ranked.head(DISPLAY_FILE_LIMIT))
            .mark_line(color="#2dd4bf", strokeWidth=2.6, point=True)
            .encode(
                x=alt.X("rank:Q", title="Risk Rank"),
                y=alt.Y("cyclomatic_avg:Q", title="Average Cyclomatic"),
                tooltip=["rank", "file", "language", "cyclomatic_avg"],
            )
            .properties(height=310)
        )
        st.altair_chart(line, use_container_width=True)

    with right:
        st.markdown("<div class='glass-panel'><b>Halstead Effort Trend (Top 50)</b></div>", unsafe_allow_html=True)
        line = (
            alt.Chart(ranked.head(DISPLAY_FILE_LIMIT))
            .mark_line(color="#38bdf8", strokeWidth=2.6, point=True)
            .encode(
                x=alt.X("rank:Q", title="Risk Rank"),
                y=alt.Y("halstead_effort:Q", title="Halstead Effort"),
                tooltip=["rank", "file", "language", "halstead_effort"],
            )
            .properties(height=310)
        )
        st.altair_chart(line, use_container_width=True)


def render_dashboard(results: list[dict[str, Any]], scope_name: str) -> None:
    frame = results_to_dataframe(results)
    if frame.empty:
        st.warning("Analysis completed but no metric rows were produced.")
        return

    st.markdown("<div class='glass-panel'><b>Summary</b></div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_kpi("Files", str(len(frame)))
    with c2:
        render_kpi("Avg Cyclomatic", f"{frame['cyclomatic_avg'].mean():.2f}")
    with c3:
        render_kpi("Avg Halstead Vol", f"{frame['halstead_volume'].mean():.1f}")
    with c4:
        render_kpi("Total Classes", str(int(frame["classes"].sum())))
    with c5:
        render_kpi("Total Methods", str(int(frame["methods"].sum())))

    render_charts(frame)

    st.caption(
        f"Showing up to {DISPLAY_FILE_LIMIT} files in UI for readability. Download Full JSON for complete report."
    )

    search = st.text_input(
        "Search files",
        placeholder="Type file path or language and press Enter",
        key="dashboard_search",
    ).strip()

    filtered_frame = frame
    if search:
        query = search.lower()
        filtered_frame = frame[
            frame["file"].str.lower().str.contains(query, na=False)
            | frame["language"].str.lower().str.contains(query, na=False)
        ]

    cyclomatic_top = (
        filtered_frame[filtered_frame["cyclomatic_avg"] > 0]
        .sort_values(["cyclomatic_avg", "cyclomatic_max"], ascending=False)
        .head(DISPLAY_FILE_LIMIT)
    )
    halstead_top = (
        filtered_frame[filtered_frame["halstead_effort"] > 0]
        .sort_values(["halstead_effort", "halstead_volume"], ascending=False)
        .head(DISPLAY_FILE_LIMIT)
    )
    oop_frame = filtered_frame.copy()
    oop_frame["oop_total"] = (
        oop_frame["classes"] + oop_frame["methods"] + oop_frame["attributes"] + oop_frame["inheritance"]
    )
    oop_top = (
        oop_frame[oop_frame["oop_total"] > 0]
        .sort_values(["oop_total", "classes", "methods"], ascending=False)
        .head(DISPLAY_FILE_LIMIT)
    )

    st.markdown("<div class='glass-panel'><b>Metric Views</b></div>", unsafe_allow_html=True)
    tab_cyclomatic, tab_halstead, tab_oop = st.tabs(["Cyclomatic", "Halstead", "OOP"])

    with tab_cyclomatic:
        if cyclomatic_top.empty:
            st.info("No files with non-zero Cyclomatic metrics for the current filter.")
        else:
            table = cyclomatic_top[["file", "language", "cyclomatic_max", "cyclomatic_avg"]]
            st.dataframe(table, use_container_width=True)

    with tab_halstead:
        if halstead_top.empty:
            st.info("No files with non-zero Halstead metrics for the current filter.")
        else:
            table = halstead_top[
                [
                    "file",
                    "language",
                    "halstead_volume",
                    "halstead_difficulty",
                    "halstead_effort",
                    "halstead_bugs",
                ]
            ]
            st.dataframe(table, use_container_width=True)

    with tab_oop:
        if oop_top.empty:
            st.info("No files with non-zero OOP metrics for the current filter.")
        else:
            table = oop_top[
                [
                    "file",
                    "language",
                    "classes",
                    "methods",
                    "attributes",
                    "inheritance",
                    "method_attribute_ratio",
                ]
            ]
            st.dataframe(table, use_container_width=True)

    raw_json = generate_json_report(results)
    summary_json = json.dumps(frame.to_dict(orient="records"), indent=2)

    st.markdown("<div class='glass-panel'><b>Exports</b></div>", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    d1.download_button(
        label=f"Download {scope_name} Full JSON",
        data=raw_json,
        file_name=f"{scope_name.lower().replace(' ', '_')}_analysis.json",
        mime="application/json",
        use_container_width=True,
    )
    d2.download_button(
        label=f"Download {scope_name} Summary JSON",
        data=summary_json,
        file_name=f"{scope_name.lower().replace(' ', '_')}_summary.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("Raw JSON"):
        st.json(results)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="glass-panel" style="text-align:center; padding:1.2rem 1rem;">
            <div style="font-size:1.1rem; font-weight:700; margin-bottom:.2rem;">No analysis yet</div>
            <div style="color:#a9b8dc;">Choose an input source, run analysis, and this space will populate with visual metrics.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_hero()

input_mode = st.radio("Input Mode", ["Uploaded Files", "GitHub Repository"], horizontal=True, label_visibility="collapsed")
results: list[dict[str, Any]] = []
summary_title = "Analysis"

if input_mode == "Uploaded Files":
    st.markdown("<div class='glass-panel'><b>Upload Source Files</b></div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload source files",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if st.button("Run Analysis", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Upload at least one supported source file.")
        else:
            with st.spinner("Analyzing uploaded files..."):
                results = run_uploaded_file_analysis(uploaded_files)
                summary_title = "Uploaded Files"

else:
    st.markdown("<div class='glass-panel'><b>Analyze GitHub Repository</b></div>", unsafe_allow_html=True)
    with st.form("repo_form", clear_on_submit=False):
        repo_url = st.text_input(
            "GitHub repository URL",
            placeholder="https://github.com/owner/repo.git",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze Repository", type="primary", use_container_width=True)

    if submitted:
        if not repo_url.strip():
            st.error("Enter a valid GitHub repository URL.")
        else:
            progress_box = st.empty()

            def progress_update(message: str) -> None:
                progress_box.info(message)

            with st.spinner("Cloning repository and running metrics..."):
                try:
                    output = analyze_github_repo(repo_url.strip(), progress_callback=progress_update)
                    st.success(
                        f"Scanned {output['total_files_scanned']} files and analyzed {output['total_files_analyzed']} files."
                    )
                    results = output.get("results", [])
                    summary_title = "GitHub Repository"
                except Exception as exc:
                    st.error(f"Repository analysis failed: {exc}")

if results:
    render_dashboard(results, summary_title)
else:
    render_empty_state()
