import json
from math import ceil

import pandas as pd
import streamlit as st

from src.data_loader import DATA, ROOT, load_catalog, load_schemes
from src.visualization import bar

ART = ROOT / "assets"
SCHEME_ART = {
    "pmuy": "household-energy.webp",
    "pmkisan": "agriculture.webp",
    "maha_dte": "education.webp",
}

with st.container(key="home_hero"):
    message, artwork = st.columns([1.05, 1], vertical_alignment="center")
    with message:
        st.title("Find government schemes in India")
        st.write("Explore benefits, check requirements and find the official place to apply.")
        with st.container(horizontal=True, key="home_actions"):
            with st.container(width="content", key="home_primary"):
                st.page_link("pages/2_Scheme_Recommendation.py", label="Get recommendations",
                             icon=":material/arrow_forward:")
            st.page_link("pages/3_Eligibility_Checker.py", label="Check eligibility",
                         icon=":material/fact_check:")
    with artwork:
        st.image(ART / "welfare-hero.webp", width="stretch")

catalog = st.cache_data(load_catalog)()
schemes = load_schemes()
scopes = "state_restricted_to_normalized"
categories = "scheme_category_clean"
national = catalog["is_national_scheme"].astype(str).str.lower().isin(["true", "1", "yes"])

a, b, c = st.columns(3)
a.metric("Kaggle catalog records", f"{len(catalog):,}", border=True)
b.metric("Catalog categories", catalog[categories].nunique(), border=True)
c.metric("Schemes with reviewed checks", len(schemes), border=True)

featured, search, analytics = st.tabs([
    ":material/explore: Reviewed schemes",
    ":material/search: Search catalog",
    ":material/monitoring: Catalog insights",
])

with featured:
    st.subheader("Schemes you can check here")
    for column, scheme in zip(st.columns(len(schemes)), schemes, strict=True):
        with column.container(border=True, key=f"scheme_card_{scheme['id']}"):
            st.image(ART / SCHEME_ART[scheme["id"]], width="stretch")
            st.caption(f'{scheme["category"]} · {scheme["state"]}')
            st.markdown(f'**{scheme["name"]}**')
            with st.expander("View benefits"):
                st.write(scheme["benefit"])
            st.page_link("pages/3_Eligibility_Checker.py", label="Check this scheme",
                         icon=":material/arrow_forward:", query_params={"scheme": scheme["id"]})


def reset_catalog_page():
    st.session_state.catalog_page = 1


with search:
    st.subheader("Search the scheme catalog")
    with st.container(border=True):
        a, b, c = st.columns([2, 1, 1])
        query = a.text_input("Scheme name", placeholder="Search by scheme name",
                             on_change=reset_catalog_page)
        choices = sorted(catalog[categories].dropna().unique())
        category = b.selectbox("Category", ["All"] + choices, on_change=reset_catalog_page)
        regions = sorted(catalog[scopes].dropna().unique())
        region_filter = c.selectbox("Listed region", ["All"] + regions, on_change=reset_catalog_page)
    matches = catalog[catalog.scheme_name.str.contains(query.strip(), case=False, regex=False, na=False)]
    if category != "All":
        matches = matches[matches[categories] == category]
    if region_filter != "All":
        matches = matches[matches[scopes] == region_filter]

    if matches.empty:
        st.info("No schemes match these filters. Try a broader search.")
    else:
        page_size = 25
        total_pages = ceil(len(matches) / page_size)
        info, pagination = st.columns([3, 1], vertical_alignment="center")
        page = pagination.number_input("Page", min_value=1, max_value=total_pages,
                                       step=1, key="catalog_page")
        offset = (page - 1) * page_size
        info.caption(f"Showing {offset + 1:,}–{min(offset + page_size, len(matches)):,} of {len(matches):,} records")
        columns = {"scheme_name": "Scheme", categories: "Category", scopes: "Listed region"}
        result = matches.iloc[offset:offset + page_size][list(columns)].rename(columns=columns)
        st.dataframe(result, hide_index=True, height=420)
        st.caption("Catalog entries may require current official verification.")

with analytics:
    st.subheader("Catalog coverage")
    first, second = st.columns(2)
    with first.container(border=True):
        st.markdown("**Schemes by category**")
        counts = catalog[categories].value_counts().head(10).rename_axis("Category").reset_index(name="Records")
        st.plotly_chart(bar(counts, "Records", "Category", orientation="h")
                        .update_yaxes(autorange="reversed"), theme=None)
    with second.container(border=True):
        st.markdown("**Schemes by state or union territory**")
        region = catalog.loc[~national, scopes].value_counts().head(10)
        counts = region.rename_axis("Listed region").reset_index(name="Records")
        st.plotly_chart(bar(counts, "Records", "Listed region", orientation="h")
                        .update_yaxes(autorange="reversed"), theme=None)
    st.caption("Counts reflect the publisher's catalog and region labels.")

    audit_path = DATA / "raw_audit.json"
    if audit_path.is_file():
        with st.expander("Dataset quality and missing values"):
            for report in json.loads(audit_path.read_text(encoding="utf-8")):
                st.markdown(f'**{report["file"]}**')
                st.caption(f'{report["rows"]:,} rows · {report["columns"]} columns · {report["duplicate_rows"]} exact duplicate rows')
                missing = pd.Series(report["missing"], name="Missing values").rename_axis("Column")
                st.dataframe(missing.reset_index(), hide_index=True)