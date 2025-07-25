# visualization_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class VisualizationPage(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        self.setup_ui()
        
    def setup_ui(self):
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Chart type selection
        ttk.Label(controls_frame, text="Chart Type:").pack(side=tk.LEFT)
        self.chart_type = ttk.Combobox(controls_frame, 
                                      values=["Bar", "Line", "Scatter", "Pie", "Histogram"])
        self.chart_type.pack(side=tk.LEFT, padx=5)
        self.chart_type.set("Bar")
        
        # Column selection
        ttk.Label(controls_frame, text="X-Axis:").pack(side=tk.LEFT, padx=5)
        self.x_column = ttk.Combobox(controls_frame)
        self.x_column.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Y-Axis:").pack(side=tk.LEFT, padx=5)
        self.y_column = ttk.Combobox(controls_frame)
        self.y_column.pack(side=tk.LEFT, padx=5)
        
        # Plot button
        self.plot_btn = ttk.Button(controls_frame, text="Generate Plot", 
                                  command=self.generate_plot)
        self.plot_btn.pack(side=tk.LEFT, padx=5)
        
        # Create figure and canvas for matplotlib
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def update_data(self):
        if self.shared_data['current_table']:
            df = pd.read_sql(f"SELECT * FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            self.x_column['values'] = list(df.columns)
            self.y_column['values'] = list(df.columns)
            
    def generate_plot(self):
        if not self.shared_data['current_table']:
            messagebox.showerror("Error", "Please select a table first!")
            return
            
        try:
            df = pd.read_sql(f"SELECT * FROM {self.shared_data['current_table']}", 
                           self.shared_data['conn'])
            
            x_col = self.x_column.get()
            y_col = self.y_column.get()
            chart_type = self.chart_type.get()
            
            self.ax.clear()
            
            if chart_type == "Bar":
                df.plot(kind='bar', x=x_col, y=y_col, ax=self.ax)
            elif chart_type == "Line":
                df.plot(kind='line', x=x_col, y=y_col, ax=self.ax)
            elif chart_type == "Scatter":
                df.plot(kind='scatter', x=x_col, y=y_col, ax=self.ax)
            elif chart_type == "Pie":
                df[y_col].value_counts().plot(kind='pie', ax=self.ax)
            elif chart_type == "Histogram":
                df[y_col].hist(ax=self.ax)
                
            self.ax.set_title(f"{chart_type} Chart: {y_col} vs {x_col}")
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {str(e)}")