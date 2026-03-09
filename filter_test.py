import tkinter as tk
import skyrim_ini_editor

root = tk.Tk()
app = skyrim_ini_editor.SkyrimINIEditor(root)
app.config.game_path='.'
app.config.documents_path='.'
app.scan_ini_files()
print('initial:', app.file_tree.get_children())
app.search_var.set('nonsense')
app.filter_file_list()
print('after_filter:', app.file_tree.get_children())
app.search_var.set('')
app.filter_file_list()
print('after_clear:', app.file_tree.get_children())
root.destroy()
