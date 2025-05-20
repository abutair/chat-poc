# load_file.py

import pandas as pd
import os

def load_filetype(file_path):
    # print("load_file.py run success")
    # Load into memory
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.xls', '.xlsx']:
        return load_excel(file_path)
    elif ext == '.csv':
        return load_csv(file_path)
    elif ext in ['.tsv', '.txt']:
        return load_tsv(file_path)
    elif ext == '.json':
        return load_json(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def load_excel(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == '.xls':
        # Force pandas to use xlrd for .xls files
        xl = pd.ExcelFile(file_path, engine='xlrd')
    else:
        # For .xlsx and others, let pandas auto-detect (defaults to openpyxl)
        xl = pd.ExcelFile(file_path)

    sheets = {sheet_name: xl.parse(sheet_name) for sheet_name in xl.sheet_names}
    return sheets


def load_csv(file_path):
    df = pd.read_csv(file_path, encoding='cp1252')
    sheets = {"Sheet1": df}
    return sheets

def load_tsv(file_path):
    df = pd.read_csv(file_path, sep="\t")
    sheets = {"Sheet1": df}
    return sheets

def load_json(file_path):
    df = pd.read_json(file_path)
    sheets = {"Sheet1": df}
    return sheets