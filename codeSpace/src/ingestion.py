import os
import glob
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from src.config import INPUT_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_and_clean_csv(file_path):
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
            
        df.replace(["#UNPARSEABLE", "#N/A", "N/A", "", " "], np.nan, inplace=True)
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        logger.error(f"Failed to read or clean CSV {file_path}: {e}")
        return pd.DataFrame()

def process_dates_and_metrics(df):
    if 'Schedule Variance' not in df.columns and 'Target Dates Variance' not in df.columns:
        if 'Variance' in df.columns:
            df['Schedule Variance'] = df['Variance'].astype(str).str.replace('d', '', case=False).str.strip()
            df['Schedule Variance'] = pd.to_numeric(df['Schedule Variance'], errors='coerce').fillna(0)
        elif 'End Date' in df.columns and 'Baseline Finish' in df.columns:
            try:
                end_dates = pd.to_datetime(df['End Date'], errors='coerce')
                baseline_dates = pd.to_datetime(df['Baseline Finish'], errors='coerce')
                df['Schedule Variance'] = (end_dates - baseline_dates).dt.days
            except Exception as e:
                logger.warning(f"Could not calculate Schedule Variance: {e}")
                df['Schedule Variance'] = 0
        else:
            df['Schedule Variance'] = 0
    else:
        var_col = 'Schedule Variance' if 'Schedule Variance' in df.columns else 'Target Dates Variance'
        df['Schedule Variance'] = pd.to_numeric(df[var_col], errors='coerce').fillna(0)

    if '% Complete' in df.columns:
        df['% Complete'] = pd.to_numeric(df['% Complete'].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    else:
        df['% Complete'] = 0

    if 'Start Date' in df.columns and 'End Date' in df.columns:
        try:
            start_dates = pd.to_datetime(df['Start Date'], errors='coerce')
            end_dates = pd.to_datetime(df['End Date'], errors='coerce')
            today = pd.to_datetime('today')
            
            total_duration = (end_dates - start_dates).dt.days
            elapsed_time = (today - start_dates).dt.days
            
            total_duration = total_duration.replace(0, 1)
            time_ratio = np.clip(elapsed_time / total_duration, 0.01, 1.0)
            df['Burn Health Ratio'] = df['% Complete'] / (time_ratio * 100)
        except Exception as e:
            logger.warning(f"Could not calculate Burn Health Ratio properly: {e}")
            df['Burn Health Ratio'] = df['% Complete'] / 100
    else:
        df['Burn Health Ratio'] = df['% Complete'] / 100

    return df

def run_ingestion_pipeline():
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    if not csv_files:
        logger.error("No CSV files found in input directory.")
        return []

    combined_data = []
    for file in csv_files:
        logger.info(f"Ingesting file: {file}")
        df = parse_and_clean_csv(file)
        if df.empty:
            continue
            
        df = process_dates_and_metrics(df)
        
        if 'Comments' not in df.columns:
            if 'Status Comment' in df.columns:
                df['Comments'] = df['Status Comment']
            elif 'Status' in df.columns:
                df['Comments'] = df['Status']
            else:
                df['Comments'] = "No comments provided."
                
        if 'Project Name' not in df.columns:
            df['Project Name'] = np.nan
        if 'Task Name' in df.columns:
            df['Project Name'] = df['Project Name'].fillna(df['Task Name'])
                
        df.fillna("Unknown", inplace=True)
        records = df.to_dict(orient='records')
        combined_data.extend(records)
        
    logger.info(f"Successfully ingested {len(combined_data)} project records.")
    return combined_data
