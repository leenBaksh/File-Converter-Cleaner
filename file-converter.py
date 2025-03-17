import io
import streamlit as st
import pandas as pd

st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files, clean data, and convert formats.")

# File Upload
files = st.file_uploader("Upload CSV or Excel Files", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]
        try:
            df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue  # Skip to the next file

        st.subheader(f"{file.name} - Preview")
        st.dataframe(df.head())

        # Data Duplicates Removal
        if st.checkbox(f"Remove Duplicates - {file.name}"):
            initial_rows = len(df)
            df = df.drop_duplicates()
            removed_rows = initial_rows - len(df)
            st.success(f"Removed {removed_rows} duplicate rows.")
            st.dataframe(df.head())

        # Fill Missing Values
        if st.checkbox(f"Fill Missing Values - {file.name}"):
            fill_method = st.selectbox(
                f"Choose fill method for {file.name}",
                ["Mean", "Median", "Mode", "Custom Value"]
            )
            
            if fill_method == "Mean":
                df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            elif fill_method == "Median":
                df.fillna(df.select_dtypes(include=["number"]).median(), inplace=True)
            elif fill_method == "Mode":
                df.fillna(df.select_dtypes(include=["number"]).mode().iloc[0], inplace=True)
            elif fill_method == "Custom Value":
                custom_value = st.text_input(f"Enter custom value for {file.name}")

                # Check if the custom value can be converted to a number
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        # If the column is numeric, convert the custom value to a float
                        try:
                            df[col].fillna(float(custom_value), inplace=True)
                        except ValueError:
                            st.warning(f"Could not convert '{custom_value}' to a number for column '{col}'. Skipping this column.")
                    else:
                        # If the column is non-numeric, fill with the custom value as-is
                        df[col].fillna(custom_value, inplace=True)
            
            st.success("Missing values filled.")
            st.dataframe(df.head())

        # Column Selection
        selected_columns = st.multiselect(
            f"Select Columns - {file.name}",
            df.columns,
            default=list(df.columns)
        )

        if not selected_columns:
            st.warning("Please select at least one column.")
            continue  # Skip to the next file
        else:
            df = df[selected_columns]
            st.dataframe(df.head())

        # Show Chart
        if st.checkbox(f"Show Chart - {file.name}"):
            # Select numeric columns and clean data
            numeric_df = df.select_dtypes(include="number")
            numeric_df = numeric_df.apply(pd.to_numeric, errors="coerce")  # Convert to numeric, coercing errors
            numeric_df = numeric_df.dropna()  # Drop rows with missing values

            if not numeric_df.empty:
                st.bar_chart(numeric_df.iloc[:, :2])  # Plot the first two numeric columns
            else:
                st.warning("No valid numeric columns found in the DataFrame.")

        # Convert File Format
        format_choice = st.radio(f"Convert {file.name} to:", ["csv", "Excel"], key=file.name)
        output = io.BytesIO()

        if format_choice == "csv":
            df.to_csv(output, index=False)
            mime = "text/csv"
            new_name = f"{file.name.split('.')[0]}.csv"
        elif format_choice == "Excel":
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            new_name = f"{file.name.split('.')[0]}.xlsx"

        output.seek(0)
        st.download_button(
            label=f"Download {new_name}",
            data=output,
            file_name=new_name,
            mime=mime
        )
        st.success("Processing Completed!")