import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

# Function to read and parse HTML content
def process_html_file(file):
    html_content = file.read().decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table rows
    tables = soup.find_all('table')
    if not tables:
        return None  # Return None if no tables are found
    first_table = tables[0]
    rows = first_table.find_all('tr')
    
    # Prepare data for CSV
    csv_data = []
    for row in rows:
        row_list = re.findall(r'>([^<]+)<', str(row))
        csv_data.append(row_list)
    
    dic = {'backtest_name':file.name.replace('.htm','')}
    for row in csv_data[5:]:
        if len(row) % 2 == 0:
            keys = row[0::2]  # Elements at even indexes
            values = row[1::2]  # Elements at odd indexes
            dic.update(dict(zip(keys, values)))
        else:
            col_prefix = row[0]
            row = row[1:]
            keys = row[0::2]  # Elements at even indexes
            keys = [col_prefix + ' ' + key for key in keys]
            values = row[1::2]  # Elements at odd indexes
            dic.update(dict(zip(keys, values)))
    
    return dic

# Streamlit app starts here
st.title("HTML to CSV Converter for Backtest Summaries")

# File uploader for multiple HTML files
uploaded_files = st.file_uploader(
    "Upload HTML files",
    type=["htm", "html"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"{len(uploaded_files)} file(s) uploaded successfully. Processing...")

    # Process each uploaded file
    all_dataframes = []
    for file in uploaded_files:
        st.write(f"Processing {file.name}...")
        result = process_html_file(file)
        if result:
            st.write(f"{file.name} completed processing successfully.")
            all_dataframes.append(pd.DataFrame([result]))
        else:
            st.warning(f"No valid table found in {file.name}. Skipping...")
    
    # Combine all results into a single DataFrame
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Display a preview of the DataFrame
        st.write("All Backtests Summary:")
        st.dataframe(combined_df)
        
        # Provide download button for the combined CSV
        csv_data = combined_df.to_csv(index=False)
        st.download_button(
            label="Download Combined CSV",
            data=csv_data,
            file_name="backtests_summaries.csv",
            mime="text/csv"
        )
    else:
        st.error("No valid data to display or download.")
