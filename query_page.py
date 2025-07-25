# query_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sqlite3
import pandas as pd
import ollama

class CSVQueryPage(ttk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        
        # Initialize SQLite connection if not exists
        if not self.shared_data['conn']:
            self.shared_data['conn'] = sqlite3.connect(':memory:')
            
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frames
        self.left_frame = ttk.Frame(self)
        self.right_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left frame components
        ttk.Label(self.left_frame, text="Load CSV Files").pack(anchor=tk.W)
        self.load_btn = ttk.Button(self.left_frame, text="Load CSV", command=self.load_csv)
        self.load_btn.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.left_frame, text="Available Tables").pack(anchor=tk.W)
        self.table_listbox = tk.Listbox(self.left_frame, height=5)
        self.table_listbox.pack(fill=tk.X, pady=5)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        
        ttk.Label(self.left_frame, text="Table Schema").pack(anchor=tk.W)
        self.schema_text = scrolledtext.ScrolledText(self.left_frame, height=10)
        self.schema_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Right frame components
        ttk.Label(self.right_frame, text="Enter your question:").pack(anchor=tk.W)
        self.query_entry = ttk.Entry(self.right_frame)
        self.query_entry.pack(fill=tk.X, pady=5)
        
        self.execute_btn = ttk.Button(self.right_frame, text="Generate SQL & Execute", 
                                    command=self.execute_query)
        self.execute_btn.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.right_frame, text="Generated SQL:").pack(anchor=tk.W)
        self.sql_text = scrolledtext.ScrolledText(self.right_frame, height=5, font=('Courier', 10))
        self.sql_text.pack(fill=tk.X, pady=5)
        
        # Configure SQL text widget tags for syntax highlighting
        self.sql_text.tag_configure('keyword', foreground='blue')
        self.sql_text.tag_configure('operator', foreground='red')
        self.sql_text.tag_configure('function', foreground='purple')
        
        ttk.Label(self.right_frame, text="Query Results:").pack(anchor=tk.W)
        self.results_text = scrolledtext.ScrolledText(self.right_frame, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def load_csv(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return
            
        try:
            # Read CSV file
            df = pd.read_csv(filepath)
            table_name = filepath.split('/')[-1].replace('.csv', '')
            
            # Store in SQLite
            df.to_sql(table_name, self.shared_data['conn'], if_exists='replace', index=False)
            
            # Update shared data
            self.shared_data['loaded_files'][table_name] = {
                'path': filepath,
                'columns': list(df.columns)
            }
            self.update_table_list()
            messagebox.showinfo("Success", f"Loaded {table_name} successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def update_table_list(self):
        self.table_listbox.delete(0, tk.END)
        for table in self.shared_data['loaded_files'].keys():
            self.table_listbox.insert(tk.END, table)
    
    def on_table_select(self, event):
        selection = self.table_listbox.curselection()
        if not selection:
            return
            
        table_name = self.table_listbox.get(selection[0])
        self.shared_data['current_table'] = table_name
        
        # Show schema
        cursor = self.shared_data['conn'].cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        schema_text = f"Table: {table_name}\nColumns:\n"
        for col in columns:
            schema_text += f"- {col[1]} ({col[2]})\n"
        
        self.schema_text.delete(1.0, tk.END)
        self.schema_text.insert(tk.END, schema_text)
    
    def format_sql(self, sql):
        """Format SQL query for better readability"""
        # List of keywords to put on new lines
        keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
        
        # Replace multiple spaces with single space
        sql = ' '.join(sql.split())
        
        # Add newlines before keywords
        formatted_sql = sql
        for keyword in keywords:
            formatted_sql = formatted_sql.replace(keyword, f'\n{keyword}')
            formatted_sql = formatted_sql.replace(keyword.lower(), f'\n{keyword}')
        
        # Remove leading newline if exists
        formatted_sql = formatted_sql.lstrip('\n')
        
        # Add proper indentation
        lines = formatted_sql.split('\n')
        indented_lines = []
        base_indent = '    '
        
        for line in lines:
            if any(line.strip().startswith(keyword) for keyword in ['WHERE', 'GROUP BY', 'HAVING', 'ORDER BY']):
                indented_lines.append(base_indent + line)
            else:
                indented_lines.append(line)
        
        return '\n'.join(indented_lines)
    
    def generate_sql_query(self, nl_query, table_name):
        if not table_name:
            raise ValueError("No table selected!")
            
        cursor = self.shared_data['conn'].cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        prompt = f"""
        Convert the following natural language request into a valid SQL query compatible with SQLite.
        Use the following table schema:
        Table: {table_name}
        Columns: {', '.join(columns)}
        
        Important: Return ONLY the SQL query without any explanations or markdown formatting.
        
        Request: "{nl_query}"
        """
        
        response = ollama.chat(model='llama3.1:latest', messages=[{"role": "user", "content": prompt}])
        sql = response['message']['content'].strip()
        
        # Clean up the response to extract just the SQL
        sql = sql.replace('```sql', '').replace('```', '')
        sql = sql.strip()
        
        # Format the SQL query
        formatted_sql = self.format_sql(sql)
        
        return formatted_sql
    
    def execute_query(self):
        if not self.shared_data['current_table']:
            messagebox.showerror("Error", "Please select a table first!")
            return
            
        nl_query = self.query_entry.get().strip()
        if not nl_query:
            messagebox.showerror("Error", "Please enter a question!")
            return
            
        try:
            # Generate SQL
            sql_query = self.generate_sql_query(nl_query, self.shared_data['current_table'])
            self.sql_text.delete(1.0, tk.END)
            self.sql_text.insert(tk.END, sql_query)
            
            # Execute query
            cursor = self.shared_data['conn'].cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            # Format results
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            
            # Display results with better formatting
            self.results_text.delete(1.0, tk.END)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.expand_frame_repr', False)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.width', None)
            formatted_df = df.to_string(index=False, justify='left')
            self.results_text.insert(tk.END, formatted_df)
            
        except Exception as e:
            messagebox.showerror("Error", f"Query execution failed: {str(e)}")