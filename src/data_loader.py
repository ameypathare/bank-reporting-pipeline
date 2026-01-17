import pandas as pd
import os
from typing import Dict, List
import json


class DataLoader:
    """Loads CSV data from the data directory"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.dataframes = {}
        
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    def load_all_csv_files(self) -> Dict[str, pd.DataFrame]:
        """Load all required CSV files from data directory"""
        csv_files = {
            'bank_data': 'bank_data.csv',
            'capital_data': 'capital_data.csv',
            'liquidity_data': 'liquidity_data.csv',
            'credit_data': 'credit_data.csv'
        }
        
        for name, filename in csv_files.items():
            filepath = os.path.join(self.data_dir, filename)
            try:
                df = pd.read_csv(filepath)
                self.dataframes[name] = df
                print(f"    Loaded {filename}: {len(df)} rows")
            except FileNotFoundError:
                print(f"    File not found: {filepath}")
                self.dataframes[name] = pd.DataFrame()
            except Exception as e:
                print(f"    Error loading {filename}: {e}")
                self.dataframes[name] = pd.DataFrame()
        
        return self.dataframes
    
    def display_data_overview(self):
        """Display overview of loaded data"""
        print("\n" + "="*70)
        print("DATA OVERVIEW")
        print("="*70)
        
        for name, df in self.dataframes.items():
            if df.empty:
                print(f"\n {name.replace('_', ' ').title()}: EMPTY")
                continue
                
            print(f"\n {name.replace('_', ' ').title()}:")
            print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"   Columns: {', '.join(df.columns.tolist())}")
    
    def get_bank_ids(self) -> List[str]:
        """Get list of all unique bank IDs"""
        if 'bank_data' in self.dataframes and not self.dataframes['bank_data'].empty:
            return self.dataframes['bank_data']['bank_id'].unique().tolist()
        return []
    
    def get_bank_data(self, bank_id: str) -> Dict:
        """
        Get all data for a specific bank across all CSV files
        Returns a dictionary with keys: bank_data, capital_data, liquidity_data, credit_data
        """
        result = {}
        
        for name, df in self.dataframes.items():
            if df.empty:
                continue
            
            if 'bank_id' in df.columns:
                bank_rows = df[df['bank_id'] == bank_id]
                if not bank_rows.empty:
                    # Convert first matching row to dict
                    result[name] = bank_rows.iloc[0].to_dict()
        
        return result
    
    def save_data_summary(self, output_file: str = "data_summary.json"):
        """Save data loading summary to JSON file"""
        summary = {
            'total_banks': len(self.get_bank_ids()),
            'bank_ids': self.get_bank_ids(),
            'files_loaded': {},
        }
        
        for name, df in self.dataframes.items():
            summary['files_loaded'][name] = {
                'rows': len(df),
                'columns': df.columns.tolist() if not df.empty else [],
                'loaded': not df.empty
            }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n Data summary saved to {output_file}")
        return summary


if __name__ == "__main__":
    # Test the data loader
    print("Testing Data Loader...")
    print("="*70)
    
    try:
        loader = DataLoader("data")
        dataframes = loader.load_all_csv_files()
        loader.display_data_overview()
        
        bank_ids = loader.get_bank_ids()
        print(f"\n Available Bank IDs: {bank_ids}")
        
        if bank_ids:
            sample_bank = bank_ids[0]
            print(f"\nSample data for {sample_bank}:")
            bank_data = loader.get_bank_data(sample_bank)
            print(json.dumps(bank_data, indent=2, default=str))
            
    except Exception as e:
        print(f"Error: {e}")