# main.py
import tkinter as tk
from tkinter import ttk
from query_page import CSVQueryPage
from visualization_page import VisualizationPage
from stats_page import StatsPage
from export_page import ExportPage

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Analysis Suite")
        self.root.geometry("1200x800")
        
        # Create shared state for data
        self.shared_data = {
            'loaded_files': {},
            'current_table': None,
            'conn': None
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create pages
        self.query_page = CSVQueryPage(self.notebook, self.shared_data)
        self.viz_page = VisualizationPage(self.notebook, self.shared_data)
        self.stats_page = StatsPage(self.notebook, self.shared_data)
        self.export_page = ExportPage(self.notebook, self.shared_data)
        
        # Add pages to notebook
        self.notebook.add(self.query_page, text="Query Data")
        self.notebook.add(self.viz_page, text="Visualize")
        self.notebook.add(self.stats_page, text="Statistics")
        self.notebook.add(self.export_page, text="Export")
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)
        
    def on_tab_change(self, event):
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")
        
        # Update current tab's data if needed
        if tab_name == "Visualize":
            self.viz_page.update_data()
        elif tab_name == "Statistics":
            self.stats_page.update_data()
        elif tab_name == "Export":
            self.export_page.update_data()

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()