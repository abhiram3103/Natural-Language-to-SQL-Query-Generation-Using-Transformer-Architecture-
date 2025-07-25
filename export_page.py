# export_page.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

class ExportPage(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        
    def setup_ui(self):
        # Export options frame
        options_frame = ttk.LabelFrame(self, text="Export Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Format selection
        ttk.Label(options_frame, text="Export Format:").pack(anchor=tk.W, padx=5, pady=5)
        self.format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(options_frame, text="CSV", variable=self.format_var, 
                       value="csv").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(options_frame, text="Excel", variable=self.format_var, 
                       value="excel").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(options_frame, text="JSON", variable=self.format_var, 
                       value="json").pack(anchor=tk.W, padx=20)
        
        # Column selection
        ttk.Label(options_frame, text="Select Columns:").pack(anchor=tk.W, padx=5, pady=5)
        self.column_listbox = tk.Listbox(options_frame, selectmode=tk.MULTIPLE, height=10)
        self.column_listbox.pack(fill=tk.X, padx=20, pady=5)
        
        # Export button
        self.export_btn = ttk.Button(self, text="Export Data", command=self.export_data)
        self.export_btn.pack(pady=10)
        
    def update_data(self):
        if self.shared_data['current_table']:
            df = pd.read_sql(f"SELECT * FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            self.column_listbox.delete(0, tk.END)
            for column in df.columns:
                self.column_listbox.insert(tk.END, column)
                
    def export_data(self):
        if not self.shared_data['current_table']:
            messagebox.showerror("Error", "Please select a table first!")
            return
            
        try:
            # Get selected columns
            selected_indices = self.column_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "Please select at least one column!")
                return
                
            selected_columns = [self.column_listbox.get(i) for i in selected_indices]
            
            # Get data
            df = pd.read_sql(f"SELECT {', '.join(selected_columns)} FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            
            # Get save location
            format_type = self.format_var.get()
            filetypes = {
                "csv": [("CSV files", "*.csv")],
                "excel": [("Excel files", "*.xlsx")],
                "json": [("JSON files", "*.json")]
            }
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=filetypes[format_type]
            )
            
            if not filepath:
                return
                
            # Export based on format
            if format_type == "csv":
                df.to_csv(filepath, index=False)
            elif format_type == "excel":
                df.to_excel(filepath, index=False)
            elif format_type == "json":
                df.to_json(filepath, orient="records")
                
            messagebox.showinfo("Success", f"Data exported successfully to {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")