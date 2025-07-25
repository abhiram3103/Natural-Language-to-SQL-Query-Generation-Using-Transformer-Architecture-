# stats_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np

class StatsPage(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        
    def setup_ui(self):
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Column selection
        ttk.Label(controls_frame, text="Select Column:").pack(side=tk.LEFT)
        self.column_combo = ttk.Combobox(controls_frame)
        self.column_combo.pack(side=tk.LEFT, padx=5)
        
        # Calculate button
        self.calc_btn = ttk.Button(controls_frame, text="Calculate Statistics", 
                                 command=self.calculate_stats)
        self.calc_btn.pack(side=tk.LEFT, padx=5)
        
        # Stats display
        self.stats_text = tk.Text(self, height=20, width=50)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def update_data(self):
        if self.shared_data['current_table']:
            df = pd.read_sql(f"SELECT * FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            self.column_combo['values'] = list(df.columns)
            
    def calculate_stats(self):
        if not self.shared_data['current_table']:
            messagebox.showerror("Error", "Please select a table first!")
            return
            
        try:
            df = pd.read_sql(f"SELECT * FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            column = self.column_combo.get()
            
            # Calculate statistics
            stats = {
                "Count": len(df[column]),
                "Unique Values": len(df[column].unique()),
                "Missing Values": df[column].isnull().sum(),
                "Data Type": str(df[column].dtype)
            }
            
            # Add numerical statistics if applicable
            if pd.api.types.is_numeric_dtype(df[column]):
                num_stats = {
                    "Mean": df[column].mean(),
                    "Median": df[column].median(),
                    "Std Dev": df[column].std(),
                    "Min": df[column].min(),
                    "Max": df[column].max(),
                    "25th Percentile": df[column].quantile(0.25),
                    "75th Percentile": df[column].quantile(0.75)
                }
                stats.update(num_stats)
            else:
                # For categorical data
                value_counts = df[column].value_counts().head()
                stats["Top Values"] = "\n".join([f"{k}: {v}" for k, v in value_counts.items()])
            
            # Display statistics
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "Statistics for column: " + column + "\n\n")
            
            for key, value in stats.items():
                if isinstance(value, float):
                    self.stats_text.insert(tk.END, f"{key}: {value:.4f}\n")
                else:
                    self.stats_text.insert(tk.END, f"{key}: {value}\n")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate statistics: {str(e)}")