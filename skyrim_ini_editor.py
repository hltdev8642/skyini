#!/usr/bin/env python3
"""
Skyrim INI File Editor
A comprehensive GUI tool for editing Skyrim configuration files.

Features:
- Path configuration with persistence
- Recursive INI file detection
- Visual property editor with type-aware widgets
- Search and filter functionality
- Graceful error handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import Dict, List, Tuple, Optional


class Config:
    """Manages application configuration persistence."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.game_path: str = ""
        self.documents_path: str = ""
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.game_path = data.get('game_path', '')
                    self.documents_path = data.get('documents_path', '')
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            data = {
                'game_path': self.game_path,
                'documents_path': self.documents_path
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


class INIFile:
    """Represents a parsed INI file with its metadata.

    The sections structure is an ordered mapping from section name to a list of
    entries. Each entry is either a comment or a property. Comments are stored
    verbatim so that the UI can display them in-place.

    Entry formats:
        {'type': 'comment', 'text': <comment text>}
        {'type': 'property', 'key': <key>, 'value': <value>, 'comments': [<comments>]}
    """
    
    def __init__(self, filepath: str, source: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.source = source  # 'game' or 'documents'
        # sections -> list of entries as described above
        self.sections: Dict[str, List[Dict]] = {}
        self.modified = False
        self.parse()
    
    def parse(self) -> None:
        """Parse the INI file, capturing comments and properties.

        We always use manual parsing so that comments are preserved and placed
        in the resulting data structure.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self._manual_parse(content)
        except Exception as e:
            print(f"Error parsing {self.filepath}: {e}")
    
    def _manual_parse(self, content: str) -> None:
        """Manual INI parsing that preserves comments and order."""
        current_section = "DEFAULT"
        self.sections = {current_section: []}
        comment_acc: List[str] = []
        
        for raw_line in content.splitlines():
            line = raw_line.rstrip('\n')
            stripped = line.strip()
            
            # Comment line
            if stripped.startswith(';') or stripped.startswith('#'):
                comment_acc.append(stripped)
                continue
            
            # Empty line
            if not stripped:
                comment_acc.append('')
                continue
            
            # Section header
            if stripped.startswith('[') and stripped.endswith(']'):
                # flush any accumulated comments as standalone entries
                if comment_acc:
                    for c in comment_acc:
                        self.sections[current_section].append({'type': 'comment', 'text': c})
                    comment_acc = []
                current_section = stripped[1:-1].strip()
                if current_section not in self.sections:
                    self.sections[current_section] = []
                continue
            
            # Key-value pair
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                entry = {
                    'type': 'property',
                    'key': key,
                    'value': value,
                    'comments': comment_acc.copy()
                }
                self.sections[current_section].append(entry)
                comment_acc = []
                continue
            
            # Anything else (malformed) treat as comment
            comment_acc.append(line)
        
        # leftover comments
        if comment_acc:
            for c in comment_acc:
                self.sections[current_section].append({'type': 'comment', 'text': c})
        
    def save(self) -> bool:
        """Save changes back to the INI file."""
        try:
            # Read original content to preserve formatting
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Build a map of section/key to new values
            current_section = "DEFAULT"
            new_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                # Preserve empty lines and comments
                if not stripped or stripped.startswith(';') or stripped.startswith('#'):
                    new_lines.append(line)
                    continue
                
                # Section header
                if stripped.startswith('[') and stripped.endswith(']'):
                    current_section = stripped[1:-1].strip()
                    new_lines.append(line)
                    continue
                # Key-value pair
                if '=' in stripped:
                    key = stripped.split('=')[0].strip()
                    # search in entries for this key
                    updated = False
                    if current_section in self.sections:
                        for entry in self.sections[current_section]:
                            if entry.get('type') == 'property' and entry.get('key') == key:
                                indent = len(line) - len(line.lstrip())
                                new_value = entry['value']
                                new_lines.append(' ' * indent + f"{key}={new_value}\n")
                                updated = True
                                break
                    if not updated:
                        new_lines.append(line)
                    continue
                
                new_lines.append(line)
            
            # Write back to file
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            self.modified = False
            return True
            
        except Exception as e:
            print(f"Error saving {self.filepath}: {e}")
            return False
    
    def set_value(self, section: str, key: str, value: str) -> None:
        """Update a property's value and mark file as modified.

        This searches the entries list for the given key.
        """
        if section in self.sections:
            for entry in self.sections[section]:
                if entry.get('type') == 'property' and entry.get('key') == key:
                    if entry.get('value') != value:
                        entry['value'] = value
                        self.modified = True
                    break


class PropertyWidget:
    """Factory for creating appropriate widgets based on value type."""
    
    @staticmethod
    def infer_type(value: str) -> str:
        """Infer the type of a value."""
        value_lower = value.lower().strip()
        
        # Boolean
        if value_lower in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
            return 'boolean'
        
        # Integer
        try:
            int(value)
            return 'integer'
        except ValueError:
            pass
        
        # Float
        try:
            float(value)
            return 'float'
        except ValueError:
            pass
        
        return 'string'
    
    @staticmethod
    def create_widget(parent: tk.Widget, value: str, callback) -> Tuple[tk.Widget, callable]:
        """
        Create appropriate widget for a value.
        Returns (widget, getter_function).
        """
        value_type = PropertyWidget.infer_type(value)
        
        if value_type == 'boolean':
            # Checkbox
            var = tk.BooleanVar()
            value_lower = value.lower().strip()
            var.set(value_lower in ('true', '1', 'yes', 'on'))
            
            widget = ttk.Checkbutton(parent, variable=var, command=callback)
            
            def getter():
                return 'true' if var.get() else 'false'
            
            return widget, getter
        
        elif value_type in ('integer', 'float'):
            # Numeric spinbox
            var = tk.StringVar(value=value)
            widget = ttk.Spinbox(
                parent,
                from_=-999999,
                to=999999,
                textvariable=var,
                width=20
            )
            widget.bind('<KeyRelease>', lambda e: callback())
            
            def getter():
                return var.get()
            
            return widget, getter
        
        else:
            # Text entry
            var = tk.StringVar(value=value)
            widget = ttk.Entry(parent, textvariable=var, width=40)
            widget.bind('<KeyRelease>', lambda e: callback())
            
            def getter():
                return var.get()
            
            return widget, getter


class CollapsibleFrame(ttk.Frame):
    """A frame that can be collapsed/expanded with a toggle button."""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.expanded = tk.BooleanVar(value=True)
        
        # Header with toggle button
        self.header = ttk.Frame(self)
        self.header.pack(fill='x', padx=2, pady=2)
        
        self.toggle_btn = ttk.Button(
            self.header,
            text='▼',
            width=3,
            command=self.toggle
        )
        self.toggle_btn.pack(side='left')
        
        self.title_label = ttk.Label(
            self.header,
            text=title,
            font=('Arial', 10, 'bold')
        )
        self.title_label.pack(side='left', padx=5)
        
        # Content frame
        self.content = ttk.Frame(self, relief='groove', borderwidth=1)
        self.content.pack(fill='both', expand=True, padx=10, pady=2)
    
    def toggle(self):
        """Toggle collapsed/expanded state."""
        if self.expanded.get():
            self.content.pack_forget()
            self.toggle_btn.configure(text='▶')
            self.expanded.set(False)
        else:
            self.content.pack(fill='both', expand=True, padx=10, pady=2)
            self.toggle_btn.configure(text='▼')
            self.expanded.set(True)


class SkyrimINIEditor:
    """Main application class."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Skyrim INI File Editor")
        self.root.geometry("1200x700")
        
        self.config = Config()
        self.ini_files: List[INIFile] = []
        self.current_file: Optional[INIFile] = None
        self.property_widgets: Dict[Tuple[str, str], callable] = {}  # (section, key) -> getter
        
        self.setup_ui()
        self.scan_ini_files()
    
    def setup_ui(self) -> None:
        """Initialize the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Configure Paths", command=self.configure_paths)
        file_menu.add_command(label="Refresh Files", command=self.scan_ini_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient='horizontal')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - File list
        left_panel = ttk.Frame(main_container, width=300)
        main_container.add(left_panel, weight=1)
        
        # Search bar
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Filter:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_file_list())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Flat / Tree view toggle
        self.flat_view_var = tk.BooleanVar(value=False)
        flat_view_toggle = ttk.Checkbutton(
            search_frame,
            text="Flat view",
            variable=self.flat_view_var,
            command=self.filter_file_list
        )
        flat_view_toggle.pack(side='left', padx=5)
        
        # Search in files button
        ttk.Button(
            search_frame,
            text="🔍",
            width=3,
            command=self.search_in_files
        ).pack(side='left')
        
        # File list
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.file_tree = ttk.Treeview(list_frame, selectmode='browse', show='tree')
        self.file_tree.pack(side='left', fill='both', expand=True)
        
        file_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        file_scrollbar.pack(side='right', fill='y')
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Right panel - Property editor
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=3)
        
        # Editor toolbar
        toolbar = ttk.Frame(right_panel)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        self.current_file_label = ttk.Label(
            toolbar,
            text="No file selected",
            font=('Arial', 10, 'bold')
        )
        self.current_file_label.pack(side='left', padx=5)
        
        ttk.Button(
            toolbar,
            text="Save",
            command=self.save_current_file
        ).pack(side='right', padx=5)
        
        self.modified_label = ttk.Label(toolbar, text="", foreground="red")
        self.modified_label.pack(side='right', padx=5)
        
        # Editor canvas with scrollbar
        editor_frame = ttk.Frame(right_panel)
        editor_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.editor_canvas = tk.Canvas(editor_frame, bg='white')
        self.editor_canvas.pack(side='left', fill='both', expand=True)
        
        editor_scrollbar = ttk.Scrollbar(
            editor_frame,
            orient='vertical',
            command=self.editor_canvas.yview
        )
        editor_scrollbar.pack(side='right', fill='y')
        self.editor_canvas.configure(yscrollcommand=editor_scrollbar.set)
        
        # Scrollable frame inside canvas
        self.editor_content = ttk.Frame(self.editor_canvas)
        self.editor_window = self.editor_canvas.create_window(
            (0, 0),
            window=self.editor_content,
            anchor='nw'
        )
        
        self.editor_content.bind('<Configure>', self.on_editor_configure)
        self.editor_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief='sunken',
            anchor='w'
        )
        self.status_bar.pack(fill='x', side='bottom')
    
    def on_editor_configure(self, event) -> None:
        """Update scroll region when editor content changes."""
        self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox('all'))
    
    def on_canvas_configure(self, event) -> None:
        """Update content width when canvas is resized."""
        self.editor_canvas.itemconfig(self.editor_window, width=event.width)
    
    def configure_paths(self) -> None:
        """Show dialog to configure paths."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Paths")
        dialog.geometry("600x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Game path
        ttk.Label(dialog, text="Game Installation Folder:").grid(
            row=0, column=0, padx=10, pady=10, sticky='w'
        )
        game_var = tk.StringVar(value=self.config.game_path)
        game_entry = ttk.Entry(dialog, textvariable=game_var, width=50)
        game_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(
            dialog,
            text="Browse",
            command=lambda: self.browse_folder(game_var)
        ).grid(row=0, column=2, padx=10, pady=10)
        
        # Documents path
        ttk.Label(dialog, text="Documents Folder:").grid(
            row=1, column=0, padx=10, pady=10, sticky='w'
        )
        docs_var = tk.StringVar(value=self.config.documents_path)
        docs_entry = ttk.Entry(dialog, textvariable=docs_var, width=50)
        docs_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(
            dialog,
            text="Browse",
            command=lambda: self.browse_folder(docs_var)
        ).grid(row=1, column=2, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        def save_paths():
            self.config.game_path = game_var.get()
            self.config.documents_path = docs_var.get()
            self.config.save()
            dialog.destroy()
            self.scan_ini_files()
        
        ttk.Button(button_frame, text="Save", command=save_paths).pack(
            side='left', padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side='left', padx=5
        )
    
    def browse_folder(self, var: tk.StringVar) -> None:
        """Show folder browser dialog."""
        folder = filedialog.askdirectory(initialdir=var.get() or os.path.expanduser('~'))
        if folder:
            var.set(folder)
    
    def scan_ini_files(self) -> None:
        """Scan configured directories for INI files and populate the tree."""
        self.ini_files.clear()
        self.status_bar.config(text="Scanning for INI files...")
        self.root.update()

        # Scan game folder
        if self.config.game_path and os.path.exists(self.config.game_path):
            self._scan_directory(self.config.game_path, 'game')
        # Scan documents folder
        if self.config.documents_path and os.path.exists(self.config.documents_path):
            self._scan_directory(self.config.documents_path, 'documents')

        # After gathering ini_files, populate tree without filter
        self.populate_file_tree()
        self.status_bar.config(text=f"Found {len(self.ini_files)} INI files")
    
    def _scan_directory(self, path: str, source: str) -> None:
        """Recursively scan directory for INI files and append to list."""
        try:
            for root_dir, dirs, files in os.walk(path):
                for filename in files:
                    if filename.lower().endswith('.ini'):
                        filepath = os.path.join(root_dir, filename)
                        try:
                            ini_file = INIFile(filepath, source)
                            self.ini_files.append(ini_file)
                        except Exception as e:
                            print(f"Error loading {filepath}: {e}")
        except Exception as e:
            print(f"Error scanning {path}: {e}")
    
    def filter_file_list(self) -> None:
        """Repopulate the file tree according to the filter term."""
        search_term = self.search_var.get().lower()
        self.populate_file_tree(search_term)
    
    def populate_file_tree(self, search_term: str = "") -> None:
        """Rebuild the INI file tree, filtering by search_term if provided.

        Supports two modes:
        - Tree view (grouped by source folder)
        - Flat view (all files listed in a single list)
        """
        self.file_tree.delete(*self.file_tree.get_children())
        flat_view = self.flat_view_var.get() if hasattr(self, 'flat_view_var') else False
        
        if flat_view:
            # Flat list: show all matching .ini files together, just like original view.
            for idx, ini in enumerate(self.ini_files):
                base_path = None
                if ini.source == 'game':
                    base_path = self.config.game_path
                elif ini.source == 'documents':
                    base_path = self.config.documents_path
                if not base_path or not os.path.exists(base_path):
                    base_path = os.path.dirname(ini.filepath)
                rel = os.path.relpath(ini.filepath, base_path)
                if search_term and search_term not in rel.lower():
                    continue
                self.file_tree.insert('', 'end', text=rel, values=(idx,))
            return
        
        def add_group(label: str, key: str, base_path: str):
            files = []
            for idx, ini in enumerate(self.ini_files):
                if ini.source != key:
                    continue
                rel = os.path.relpath(ini.filepath, base_path)
                if not search_term or search_term in rel.lower():
                    files.append((idx, rel))
            if not files:
                return
            
            root_node = self.file_tree.insert('', 'end', text=f"{label} ({len(files)} files)", open=True)
            # Build a nested tree based on path segments
            nodes = {(): root_node}
            for idx, rel in sorted(files, key=lambda x: x[1].lower()):
                parts = rel.replace('\\', '/').split('/')
                parent_key = ()
                for part in parts[:-1]:
                    parent_key = parent_key + (part,)
                    if parent_key not in nodes:
                        nodes[parent_key] = self.file_tree.insert(
                            nodes[parent_key[:-1]],
                            'end',
                            text=part,
                            open=False
                        )
                # Insert file leaf
                file_key = tuple(parts)
                self.file_tree.insert(
                    nodes[parent_key],
                    'end',
                    text=parts[-1],
                    values=(idx,)
                )
        
        if self.config.game_path and os.path.exists(self.config.game_path):
            add_group('Game Folder', 'game', self.config.game_path)
        if self.config.documents_path and os.path.exists(self.config.documents_path):
            add_group('Documents Folder', 'documents', self.config.documents_path)
    
    def search_in_files(self) -> None:
        """Search for keys or values across all INI files."""
        search_term = tk.simpledialog.askstring(
            "Search in Files",
            "Enter search term (key or value):",
            parent=self.root
        )
        
        if not search_term:
            return
        
        search_term = search_term.lower()
        results = []
        
        for ini_file in self.ini_files:
            for section, entries in ini_file.sections.items():
                for entry in entries:
                    if entry.get('type') == 'property':
                        key = entry['key']
                        value = entry.get('value', '')
                        if search_term in key.lower() or search_term in value.lower():
                            results.append({
                                'file': ini_file.filename,
                                'path': ini_file.filepath,
                                'section': section,
                                'key': key,
                                'value': value
                            })
        
        # Show results dialog
        self.show_search_results(search_term, results)
    
    def show_search_results(self, search_term: str, results: List[Dict]) -> None:
        """Display search results in a dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Search Results: '{search_term}'")
        dialog.geometry("800x500")
        
        ttk.Label(
            dialog,
            text=f"Found {len(results)} matches",
            font=('Arial', 10, 'bold')
        ).pack(padx=10, pady=10)
        
        # Results tree
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('file', 'section', 'key', 'value')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        tree.heading('file', text='File')
        tree.heading('section', text='Section')
        tree.heading('key', text='Key')
        tree.heading('value', text='Value')
        
        tree.column('file', width=200)
        tree.column('section', width=150)
        tree.column('key', width=200)
        tree.column('value', width=200)
        
        for result in results:
            tree.insert('', 'end', values=(
                result['file'],
                result['section'],
                result['key'],
                result['value']
            ))
        
        tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def on_file_select(self, event) -> None:
        """Handle file selection in tree."""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.file_tree.item(item, 'values')
        
        if not values:
            return  # Parent node selected
        
        # Check for unsaved changes
        if self.current_file and self.current_file.modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes to {self.current_file.filename}?",
                parent=self.root
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_current_file()
        
        # Load selected file
        file_index = int(values[0])
        self.load_file(self.ini_files[file_index])
    
    def load_file(self, ini_file: INIFile) -> None:
        """Load an INI file into the editor."""
        self.current_file = ini_file
        self.property_widgets.clear()
        
        # Clear editor
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        # Update header
        self.current_file_label.config(text=ini_file.filename)
        self.update_modified_indicator()
        
        # Create sections
        if not ini_file.sections:
            ttk.Label(
                self.editor_content,
                text="No properties found in this file",
                font=('Arial', 10, 'italic')
            ).pack(padx=10, pady=20)
            return
        
        for section_name, entries in ini_file.sections.items():
            if not entries:
                continue
            
            # Create collapsible section
            section_frame = CollapsibleFrame(self.editor_content, section_name)
            section_frame.pack(fill='x', padx=5, pady=5)
            
            # Add entries (comments & properties)
            for entry in entries:
                if entry.get('type') == 'comment':
                    # display comment label
                    comment_text = entry.get('text', '')
                    lbl = ttk.Label(
                        section_frame.content,
                        text=comment_text,
                        font=('Arial', 9, 'italic'),
                        foreground='gray'
                    )
                    lbl.pack(fill='x', padx=10, pady=1)
                    continue
                if entry.get('type') == 'property':
                    # show any comments associated with this property
                    for c in entry.get('comments', []):
                        lbl = ttk.Label(
                            section_frame.content,
                            text=c,
                            font=('Arial', 9, 'italic'),
                            foreground='gray'
                        )
                        lbl.pack(fill='x', padx=10, pady=1)
                    key = entry['key']
                    value = entry.get('value', '')
                    prop_frame = ttk.Frame(section_frame.content)
                    prop_frame.pack(fill='x', padx=5, pady=2)
                    
                    # Key label
                    key_label = ttk.Label(
                        prop_frame,
                        text=f"{key}:",
                        width=30,
                        anchor='e'
                    )
                    key_label.pack(side='left', padx=5)
                    
                    # Value widget
                    widget, getter = PropertyWidget.create_widget(
                        prop_frame,
                        value,
                        lambda s=section_name, k=key: self.on_property_change(s, k)
                    )
                    widget.pack(side='left', padx=5)
                    
                    # Store getter
                    self.property_widgets[(section_name, key)] = getter
        
        self.status_bar.config(text=f"Loaded {ini_file.filepath}")
    
    def on_property_change(self, section: str, key: str) -> None:
        """Handle property value change."""
        if not self.current_file:
            return
        
        getter = self.property_widgets.get((section, key))
        if getter:
            new_value = getter()
            self.current_file.set_value(section, key, new_value)
            self.update_modified_indicator()
    
    def update_modified_indicator(self) -> None:
        """Update the modified indicator."""
        if self.current_file and self.current_file.modified:
            self.modified_label.config(text="● Modified")
        else:
            self.modified_label.config(text="")
    
    def save_current_file(self) -> None:
        """Save the current file."""
        if not self.current_file:
            messagebox.showinfo("No File", "No file is currently open.", parent=self.root)
            return
        
        if not self.current_file.modified:
            messagebox.showinfo(
                "No Changes",
                "No changes to save.",
                parent=self.root
            )
            return
        
        # Get current values from widgets
        for (section, key), getter in self.property_widgets.items():
            value = getter()
            self.current_file.set_value(section, key, value)
        
        # Save file
        if self.current_file.save():
            self.update_modified_indicator()
            self.status_bar.config(text=f"Saved {self.current_file.filepath}")
            messagebox.showinfo(
                "Success",
                f"Successfully saved {self.current_file.filename}",
                parent=self.root
            )
        else:
            messagebox.showerror(
                "Error",
                f"Failed to save {self.current_file.filename}",
                parent=self.root
            )
    
    def show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Skyrim INI File Editor\n\n"
            "A comprehensive tool for editing Skyrim configuration files.\n\n"
            "Features:\n"
            "• Path configuration with persistence\n"
            "• Recursive INI file detection\n"
            "• Type-aware property editing\n"
            "• Search and filter functionality\n"
            "• Graceful error handling\n\n"
            "Version 1.0",
            parent=self.root
        )


def main():
    """Application entry point."""
    root = tk.Tk()
    app = SkyrimINIEditor(root)
    
    # Handle window close
    def on_closing():
        if app.current_file and app.current_file.modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Save changes to {app.current_file.filename}?",
                parent=root
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                app.save_current_file()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
