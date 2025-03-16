import io
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files, clean data, and convert formats.")

# File Upload
files = st.file_uploader("Upload CSV or Excel Files", type=["csv", "xlsx"], accept_multiple_files=True)

if files :
    for file in files:
        ext = file.name.split(".")[-1]
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)
        
        st.subheader(f"{file.name} - preview")
        st.dataframe(df.head())
        
        # Data Duplicates Removal
        if st.checkbox(f"Remove Dupicates - {file.name}"):
            df = df.drop_duplicates()
            st.success("Duplicated Removed")
            st.dataframe(df.head())
            
            #  Fill Missing Values
            if st.checkbox(f"Fil Missing values - {file.name}"):
                means = df.select_dtypes(include=["number"]).mean()
                df.fillna(means, inplace=True)
                st.success("Missing Values Filled with Mean")
                st.dataframe(df.head())
                
                # Column Selection
                # Assuming 'file' is your uploaded file and df is your DataFrame
                # Example: df = pd.read_csv(file)
                
                # Convert df.columns to a list for the default parameter
                
                selected_columns = st.multiselect(
                    f"Select Columns - {file.name}",
                    df.columns, 
                    default=list(df.columns)   # Convert to list here
                )

                # Check if any columns are selected  
                
                if selected_columns:
                    df = df[selected_columns]  # Filter the DataFrame based on selected columns
                    st.dataframe(df.head())  # Display the first few rows of the filtered DataFrame
                    
                else:
                    st.warning("Please select at least one column.")   # Handle the case where no columns are selected   
                
                    
                # Show Chart    

                if st.checkbox(f"Show Chart - {file.name}"):
                    numeric_df = df.select_dtypes(include="number")
                    if not numeric_df.empty:
                        st.bar_chart(numeric_df.iloc[:, :2])  # Plot the first two numeric column
                        
                    else:
                        st.warning("No numeric columns found in the DataFrame.")          
                        
                # Example: Assuming 'df' is your DataFrame and 'format_choice' is the user's selected format
                # Convert File format
                format_choice = st.radio(f"Convert {file.name} to:", ["csv", "Excel"], key=file.name)# or "Excel", based on user input
                
                # Create a file-like object in memory
                output = io.BytesIO()
                
                if format_choice == "csv":
                    # Convert DataFrame to CSV
                    df.to_csv(output, index=False) # Write the DataFrame to the file-like object
                    mime = "text/csv"
                    new_name = f"{file.name.split('.')[0]}.csv"  # Use the original file name with .csv extension
                
                elif format_choice == "Excel":
                    # Convert DataFrame to Excel
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False)
                        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        new_name = f"{file.name.split('.')[0]}.xlsx"  # Use the original file name with .xlsx extension

                # Reset the file pointer to the beginning of the file-like object
                output.seek(0)
                
                # Add a download button
                st.download_button(
                    label=f"Download {new_name}",  # Corrected parameter name
                    data=output,
                    file_name=new_name,
                    mime=mime
                )

                # Display a success message
                st.success("Processing Completed!")