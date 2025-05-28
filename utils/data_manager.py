import pandas as pd
import os
from datetime import datetime
import csv

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.rejections_file = os.path.join(self.data_dir, "rejections.csv")
        self.types_file = os.path.join(self.data_dir, "rejection_types.csv")
        self.modules_file = os.path.join(self.data_dir, "modules.csv")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist"""
        
        # Initialize rejections.csv
        if not os.path.exists(self.rejections_file):
            rejections_headers = ['date', 'module', 'rejection_type', 'quantity', 'reason', 'operator', 'shift']
            with open(self.rejections_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(rejections_headers)
        
        # Initialize rejection_types.csv
        if not os.path.exists(self.types_file):
            types_headers = ['name', 'description', 'created_date']
            with open(self.types_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(types_headers)
        
        # Initialize modules.csv
        if not os.path.exists(self.modules_file):
            modules_headers = ['name', 'description', 'created_date']
            with open(self.modules_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(modules_headers)
    
    def load_rejections(self):
        """Load rejection data from CSV"""
        try:
            df = pd.read_csv(self.rejections_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=['date', 'module', 'rejection_type', 'quantity', 'reason', 'operator', 'shift'])
    
    def load_rejection_types(self):
        """Load rejection types from CSV"""
        try:
            df = pd.read_csv(self.types_file)
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=['name', 'description', 'created_date'])
    
    def load_modules(self):
        """Load modules from CSV"""
        try:
            df = pd.read_csv(self.modules_file)
            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=['name', 'description', 'created_date'])
    
    def add_rejection(self, module, rejection_type, quantity, reason, operator, shift):
        """Add a new rejection record"""
        try:
            new_record = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'module': module,
                'rejection_type': rejection_type,
                'quantity': quantity,
                'reason': reason,
                'operator': operator,
                'shift': shift
            }
            
            # Append to CSV
            with open(self.rejections_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_record.keys())
                writer.writerow(new_record)
            
            return True, "Rejection record added successfully"
        except Exception as e:
            return False, f"Error adding rejection: {str(e)}"
    
    def add_rejection_type(self, name, description):
        """Add a new rejection type"""
        try:
            # Check if type already exists
            existing_types = self.load_rejection_types()
            if not existing_types.empty and name in existing_types['name'].values:
                return False, "Rejection type already exists"
            
            new_type = {
                'name': name,
                'description': description,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Append to CSV
            with open(self.types_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_type.keys())
                writer.writerow(new_type)
            
            return True, "Rejection type added successfully"
        except Exception as e:
            return False, f"Error adding rejection type: {str(e)}"
    
    def add_module(self, name, description):
        """Add a new module"""
        try:
            # Check if module already exists
            existing_modules = self.load_modules()
            if not existing_modules.empty and name in existing_modules['name'].values:
                return False, "Module already exists"
            
            new_module = {
                'name': name,
                'description': description,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Append to CSV
            with open(self.modules_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_module.keys())
                writer.writerow(new_module)
            
            return True, "Module added successfully"
        except Exception as e:
            return False, f"Error adding module: {str(e)}"
    
    def delete_rejection_type(self, name):
        """Delete a rejection type"""
        try:
            df = self.load_rejection_types()
            if df.empty or name not in df['name'].values:
                return False, "Rejection type not found"
            
            # Remove the type and save
            df = df[df['name'] != name]
            df.to_csv(self.types_file, index=False)
            
            return True, "Rejection type deleted successfully"
        except Exception as e:
            return False, f"Error deleting rejection type: {str(e)}"
    
    def delete_module(self, name):
        """Delete a module"""
        try:
            df = self.load_modules()
            if df.empty or name not in df['name'].values:
                return False, "Module not found"
            
            # Remove the module and save
            df = df[df['name'] != name]
            df.to_csv(self.modules_file, index=False)
            
            return True, "Module deleted successfully"
        except Exception as e:
            return False, f"Error deleting module: {str(e)}"
    
    def get_rejection_summary(self, start_date=None, end_date=None):
        """Get rejection summary for email reports"""
        try:
            df = self.load_rejections()
            if df.empty:
                return None
            
            # Filter by date if provided
            if start_date and end_date:
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            if df.empty:
                return None
            
            summary = {
                'total_rejections': len(df),
                'total_quantity': df['quantity'].sum(),
                'by_module': df.groupby('module')['quantity'].sum().to_dict(),
                'by_type': df.groupby('rejection_type')['quantity'].sum().to_dict(),
                'recent_records': df.nlargest(5, 'date').to_dict('records')
            }
            
            return summary
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None
