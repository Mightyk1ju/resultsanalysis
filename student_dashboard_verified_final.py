import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px

def load_and_clean_data(file):
    """
    Loads an Excel (.xlsx) or CSV (.csv) file and attempts to find a header row
    containing 'Name' and 'Class'. Cleans column names by stripping whitespace
    and converting to lowercase for internal use, but retains original casing
    for display purposes.
    """
    if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        # Handle Excel files
        xls = pd.ExcelFile(file)
        sheets = xls.sheet_names
        parser_func = lambda sheet_name, header_val: xls.parse(sheet_name=sheet_name, header=header_val)
    elif file.type == "text/csv":
        # Handle CSV files
        sheets = [None] # CSVs don't have sheets, so we can iterate once
        parser_func = lambda sheet_name, header_val: pd.read_csv(file, header=header_val)
    else:
        raise ValueError("Unsupported file type. Please upload an Excel (.xlsx) or CSV (.csv) file.")

    for sheet in sheets:
        for header_row_index in range(10): # Check first 10 rows for header
            try:
                # Attempt to parse the file with the current header_row_index
                df_try = parser_func(sheet, header_row_index)
                
                # Check for 'Name' and 'Class' columns (case-insensitive, trimmed)
                colnames_cleaned = [str(c).strip().lower() for c in df_try.columns]
                if 'name' in colnames_cleaned and 'class' in colnames_cleaned:
                    df = df_try.copy()
                    # Clean column names by stripping whitespace
                    df.columns = [str(c).strip() for c in df.columns]
                    # Drop any rows that are entirely NaN (often remaining empty rows after header detection)
                    df.dropna(how='all', inplace=True)
                    
                    # Return the DataFrame, the sheet name (or "N/A" for CSV), and the detected header row index
                    return df, sheet if sheet is not None else "N/A", header_row_index
            except Exception as e:
                # If parsing fails or columns are not found, continue to the next header row/sheet
                # print(f"Debug: Attempt with header_row {header_row_index} on sheet {sheet} failed: {e}")
                continue # Try next header row or sheet

    # If no valid header is found after checking all attempts
    raise ValueError("No valid header with 'Name' and 'Class' found in the first 10 rows of any sheet.")

# --- Helper Functions ---
def mark_to_al(subject, mark):
    """
    Converts a subject mark to its corresponding AL category.
    Subject names are expected to be the display names (e.g., 'English', 'Fn Math').
    """
    if pd.isna(mark): return None
    # Ensure mark is numeric
    try:
        mark = float(mark)
    except ValueError:
        return None # Handle non-numeric marks

    if subject.startswith("Fn "):  # Foundation Subjects
        if mark >= 75: return 'A'
        elif mark >= 30: return 'B'
        else: return 'C'
    elif subject in ['HCL', 'HML', 'HTL']:  # Higher Mother Tongue
        if mark >= 80: return 'Distinction'
        elif mark >= 65: return 'Merit'
