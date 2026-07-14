import streamlit as st
import pandas as pd
import pathlib 
import datetime as dt

st.set_page_config(page_title="Document numbers Look up tool", layout="wide")
st.title("Regulatory Index")
st.caption("For internal use only — Regulatory lookup tool (beta version)")

st.divider()

DATA_FILE = "Look_up_table_source_data.xlsx"
DATA_PATH = pathlib.Path(DATA_FILE)

# Load data
df = None 
if DATA_PATH.exists():
    try:
        df = pd.read_excel(DATA_PATH) #reads the first sheet by default 
        # st.success("Excel sheet loaded successfully")
        # st.dataframe(df, use_container_width=True) #displays the data table
    except Exception as e:
        st.error(f"Couldn't load excel file: {e}")
else:
    st.warning(f"`{DATA_FILE}` not found in the same folder as `app.py`.")

#Setting up the search feature
if df is not None and not df.empty:
    list_of_categories = ["Search all categories"] + list(df.columns)

    data_category = st.selectbox( #search categories- should match column headings of spreasheet
        "Category of input data (optional):",
        options= list_of_categories,
        index = 0 #index argument chooses which item is selected by default
    )
    
    reference = st.text_input("Input Data number/name:") #input doc ref number or device name
    show_all = st.checkbox("All Values")
    
    return_categories = ["Return all attributes"] + list(df.columns)

    return_category = st.multiselect( #search categories- should match column headings of spreasheet
        "Return data from the following categories (optional):",
        options= return_categories,
        default = ["Return all attributes"] 
    )
    
    do_search =st.button("Search", type="primary") #search button

    st.divider()

    # Run search when button is pressed
    if do_search:
        search_term = reference.strip().lower()
        mapping_mode = show_all

        if not reference.strip() and not mapping_mode: #if search button is pressed but there is no reference number
            st.warning("Please enter a Data number/name to search")
        else:    
            if mapping_mode:
                results = df.copy()

            elif data_category == "Search all categories":
                mask = df.apply(lambda col: col.astype(str).str.contains(reference.strip(), case=False, na=False))
                results = df.loc[mask.any(axis=1)].copy()

            else: #case insensitive search
                series = df[data_category].astype(str) #converts every value in the column into a string
                mask = series.str.contains(reference, case=False, na=False) # case=false makes it case insesnitive, na=false treats missing values as not matching instead of error
                results = df.loc[mask].copy() #filters data frame, keeping only rows wehere mask is true

            if "Return all attributes" not in return_category:
                if mapping_mode:
                    selected_cols = [col for col in return_category if col in results.columns]
                    if data_category != "Search all categories" and data_category in results.columns:
                        ordered_cols = [data_category] + [col for col in selected_cols if col != data_category]
                    else: 
                        ordered_cols = selected_cols
                    results = results[ordered_cols]
                else:
                    essential_cols = ["Product Name", "TD"]   # adjust for your exact names
                    selected_cols = [col for col in return_category if col in results.columns]
                    results = results[list(set(essential_cols + selected_cols))]

            st.subheader("Results")

            if results.empty:
                st.info("No records found")
            else:
                st.download_button(
                    "Download results (CSV)",
                    results.to_csv(index=False).encode("utf-8"),
                    file_name= "lookup_results.csv",
                    mime= "text/csv",
                )

                if mapping_mode:
                    st.dataframe(results, use_container_width=True)

                else: ## st.dataframe(results, use_container_width=True)
                    for _, row in results.iterrows():
                        title = f"📄 {row['TD']} | {row['Product Name']} | Class: {row.get('EU MDR Class', '-')}"  # adjust column name if needed
                        with st.expander(title):

                            if "Return all attributes" in return_category or "BUDI-DIs" in return_category:
                                st.markdown("**BUDI-DIs:**")
                                for b in str(row['BUDI-DIs']).split("\n"):
                                    if b.strip():
                                        st.markdown(f"- {b}")
                            if "Return all attributes" in return_category or "Product codes / SKU ref" in return_category:
                                st.markdown("**SKUs (Product codes):**")
                                for s in str(row['Product codes / SKU ref']).split("\n"):
                                    if s.strip():
                                        st.markdown(f"- {s}")
                            
                            # Only show "Documents" section if relevant fields exist
                            if "Return all attributes" in return_category or any(
                                col in return_category for col in ["WCH TD Number", "EU DoC number", "SSCP", "IFU", "PIL", "CER"]
                            ):
                                st.markdown("**Documents:**")
                                if "Return all attributes" in return_category or "WCH TD Number" in return_category:
                                    st.markdown(f"- WCH TD Number: {row.get('WCH TD Number', 'N/A')}")
                                if "Return all attributes" in return_category or "EU DoC number" in return_category:
                                    st.markdown(f"- EU DoC Number: {row.get('EU DoC number', 'N/A')}")

                            if "Return all attributes" in return_category or "SSCP" in return_category:
                                st.markdown(f"- SSCP: {row['SSCP']}")
                            if "Return all attributes" in return_category or "IFU" in return_category:
                                st.markdown(f"- IFU: {row['IFU']}")
                            if "Return all attributes" in return_category or "PIL" in return_category:
                                st.markdown(f"- PIL: {row['PIL']}")
                            if "Return all attributes" in return_category or "CER" in return_category:
                                st.markdown(f"- CER: {row['CER']}")

                            if "Return all attributes" in return_category or "EU MDR Class" in return_category:
                                st.markdown("**Device Class:**")
                                st.markdown(f"Classification: {row['EU MDR Class']}")

        
                            st.markdown("---")
    
    st.sidebar.subheader("Data Tools")
    with st.sidebar.expander("View/ Download full data table"):
        st.dataframe(df, use_container_width=True)

#status panael to debug paths/ file presence 
with st.sidebar.expander("Status Panel for debugging paths/file presence"):
    st.write(f"Working directory: '{pathlib.Path.cwd()}'") ##
    st.write(f"Expected data file: '{DATA_PATH.resolve()}'")
    st.write(f"Exists: '{DATA_PATH.exists()}'")
    if DATA_PATH.exists():
        stat = DATA_PATH.stat()
        st.write(f"Size: {stat.st_size} bytes")
        st.write(f"Last modified: {dt.datetime.fromtimestamp(stat.st_mtime)}")
