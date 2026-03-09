# Skyrim INI File Editor

A comprehensive, production-quality GUI application for editing Skyrim configuration files with advanced features and robust error handling.

## Features

### 🎯 Core Functionality
- **Path Configuration**: Set and persist game installation and documents folder paths
- **Automatic INI Detection**: Recursively scans both directories for all `.ini` files
- **Intelligent Parsing**: Handles both well-formed and malformed INI files gracefully
- **Comment Support**: Parses comments and displays them inline above settings in the editor
- **Type-Aware Editing**: Automatically creates appropriate widgets based on value types:
  - ✓ Checkboxes for boolean values (true/false, 1/0, yes/no, on/off)
  - ✓ Spinboxes for numeric values (integers and floats)
  - ✓ Text entries for strings
- **Organized Layout**: Collapsible section headers for clean organization
- **Change Tracking**: Visual indicators for unsaved modifications
- **Format Preservation**: Saves changes while preserving original file formatting

### 🔍 Search & Filter
- **File List Filter**: Real-time filtering of files by name
- **Search in Files**: Cross-file search for keys and values with detailed results
- **Result Navigation**: Easy-to-read search results with file, section, key, and value columns

### 🛡️ Robustness
- **Error Handling**: Graceful handling of missing paths, unreadable files, and malformed INI content
- **Unsaved Changes Protection**: Warns before switching files or closing with unsaved changes
- **Configuration Persistence**: Automatically saves and loads path configuration
- **No Crashes**: Comprehensive exception handling throughout the application

## Installation

### Requirements
- Python 3.6 or higher (tkinter included in standard Python distribution)
- No additional packages required! Uses only Python standard library.

### Quick Start

1. **Save the file**: The application is provided as a single file: `skyrim_ini_editor.py`

2. **Run the application**:
   ```bash
   python skyrim_ini_editor.py
   ```
   
   Or on Windows, double-click the file if `.py` files are associated with Python.

## Usage Guide

### First Time Setup

1. **Configure Paths**:
   - Click `File → Configure Paths` in the menu
   - Set your **Game Installation Folder** (e.g., `C:/Program Files/Steam/steamapps/common/Skyrim Special Edition`)
   - Set your **Documents Folder** (e.g., `C:/Users/YourName/Documents/My Games/Skyrim Special Edition`)
   - Click **Save**

2. **Browse Files**:
   - The application will automatically scan both directories
   - Files are grouped under "Game Folder" and "Documents Folder"
   - Click any file to load it into the editor

### Editing INI Files

1. **Select a File**: Click any INI file in the left sidebar
2. **Edit Properties**:
   - Boolean values use checkboxes
   - Numeric values use spinboxes (you can type or use arrows)
   - String values use text entry fields
3. **Expand/Collapse Sections**: Click the ▼/▶ button next to section names
4. **Save Changes**: Click the **Save** button in the toolbar
   - Modified files show a red "● Modified" indicator

### Searching

**Filter Files by Name**:
- Type in the "Filter:" search box at the top of the file list
- Files are filtered in real-time as you type

**Search Across All Files**:
- Click the 🔍 button next to the filter box
- Enter a search term (searches both keys and values)
- View results in a detailed table showing file, section, key, and value

### Tips

- **Unsaved Changes**: The application warns you before switching files or closing with unsaved changes
- **Malformed Files**: The editor handles malformed INI files using a fallback parser
- **Refresh**: Use `File → Refresh Files` to rescan directories after adding new files
- **Persistent Configuration**: Your path settings are saved in `config.json` and loaded automatically

## Architecture

### Code Structure

The application is organized into several classes for maintainability:

- **Config**: Manages configuration persistence (paths stored in `config.json`)
- **INIFile**: Represents a parsed INI file with metadata and change tracking
- **PropertyWidget**: Factory for creating type-appropriate widgets
- **CollapsibleFrame**: Custom widget for expandable/collapsible sections
- **SkyrimINIEditor**: Main application class coordinating all components

### Error Handling

The application includes comprehensive error handling:
- File I/O errors are caught and logged without crashing
- Malformed INI files fall back to manual parsing
- Missing paths are handled gracefully
- Invalid numeric inputs are accepted as strings

### File Format Preservation

When saving changes:
- Original file formatting is preserved (spacing, comments, line breaks)
- Only modified values are updated
- Comments and empty lines remain intact
- Section order is maintained

## Troubleshooting

**Problem**: No files appear after setting paths
- **Solution**: Check that the paths are correct and contain `.ini` files. Use `File → Refresh Files` to rescan.

**Problem**: Changes aren't saved
- **Solution**: Ensure you have write permissions to the file. Run as administrator if needed.

**Problem**: Application won't start
- **Solution**: Verify Python 3.6+ is installed. Check that tkinter is available (usually included with Python).

**Problem**: Some INI files won't load
- **Solution**: The application should handle malformed files gracefully. Check the console output for error messages.

## Technical Details

### Dependencies
- **tkinter**: GUI framework (included with Python)
- **configparser**: INI parsing (Python standard library)
- **json**: Configuration persistence (Python standard library)
- **pathlib/os**: File system operations (Python standard library)

### Configuration File
The application creates a `config.json` file in the same directory to store:
```json
{
  "game_path": "C:/Program Files/Steam/steamapps/common/Skyrim Special Edition",
  "documents_path": "C:/Users/YourName/Documents/My Games/Skyrim Special Edition"
}
```

### Supported Value Types
- **Boolean**: true, false, 1, 0, yes, no, on, off (case-insensitive)
- **Integer**: Whole numbers (e.g., 100, -5, 0)
- **Float**: Decimal numbers (e.g., 1.5, -0.25, 3.14159)
- **String**: Any other text value

## License

This is a single-file application created as a development tool. Free to use and modify as needed.

## Version History

**v1.0** - Initial release
- Complete INI editing functionality
- Path configuration and persistence
- Search and filter capabilities
- Robust error handling
- Type-aware property editing
- Collapsible sections
