# Quick Start Guide

## Running the Skyrim INI Editor

### Method 1: Direct Execution
```bash
python skyrim_ini_editor.py
```

### Method 2: Windows Double-Click
Simply double-click `skyrim_ini_editor.py` if Python is installed and `.py` files are associated with Python.

## Testing with Sample File

A sample INI file (`sample_skyrim.ini`) is included in this directory for testing.

### Quick Test Steps:

1. **Launch the application**:
   ```bash
   python skyrim_ini_editor.py
   ```

2. **Configure paths** (for testing):
   - Click `File → Configure Paths`
   - For "Game Installation Folder", click Browse and select this directory
   - For "Documents Folder", click Browse and select this directory
   - Click **Save**

3. **The app will scan and find `sample_skyrim.ini`**

4. **Click on the file** to load it into the editor

5. **Try editing**:
   - ✓ Toggle the `bFull Screen` checkbox
   - ✓ Change `iDifficulty` numeric value
   - ✓ Modify `sLanguage` text
   - ✓ Expand/collapse sections with ▼/▶ buttons

6. **Test search**:
   - Type "screen" in the Filter box to filter files
   - Click 🔍 and search for "Language" to search across files

7. **Save changes**:
   - Click the **Save** button
   - Check that `sample_skyrim.ini` was updated

## For Actual Skyrim Usage

### Typical Path Locations:

**Steam - Game Installation**:
```
C:\Program Files (x86)\Steam\steamapps\common\Skyrim Special Edition
```
or
```
C:\Program Files\Steam\steamapps\common\Skyrim Special Edition
```

**Documents Folder**:
```
C:\Users\[YourUsername]\Documents\My Games\Skyrim Special Edition
```

### Important INI Files

The most commonly edited Skyrim INI files are:
- `Skyrim.ini` - Main game settings
- `SkyrimPrefs.ini` - Graphics and interface preferences
- `SkyrimCustom.ini` - User custom overrides (takes precedence)

These files are typically found in the Documents folder.

## Features Showcase

### Type-Aware Editing
- **Boolean values** like `bFull Screen=false` → Checkbox
- **Numbers** like `iDifficulty=2` → Spinbox
- **Text** like `sLanguage=ENGLISH` → Text entry

### Search Capabilities
- **Filter files**: Type in the search box to instantly filter the file list
- **Search in files**: Click 🔍 to search for any key or value across all INI files

### Safety Features
- **Unsaved changes warning**: Prompted before switching files or closing
- **Format preservation**: Original file formatting, comments, and spacing preserved
- **Error handling**: Malformed INI files are handled gracefully

## Troubleshooting

**Issue**: Application doesn't start
```bash
# Check Python version (need 3.6+)
python --version

# Verify tkinter is available
python -c "import tkinter; print('tkinter OK')"
```

**Issue**: No files appearing
- Ensure the paths you configured actually exist
- Check these paths contain `.ini` files
- Use `File → Refresh Files` to rescan

**Issue**: Can't save changes
- Check file permissions (may need to run as administrator)
- Verify the file isn't open in another program
- Check disk space

## Configuration File

Settings are saved in `config.json` in the same directory:
```json
{
  "game_path": "C:/...",
  "documents_path": "C:/..."
}
```

You can manually edit this file if needed, or delete it to reset.

## Development Notes

The application is self-contained:
- ✅ Single file - complete application
- ✅ No external dependencies (uses Python standard library only)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Production-ready error handling
- ✅ Clean, maintainable code

## Next Steps

1. Configure your actual Skyrim paths
2. Browse and edit your real INI files
3. Always backup important files before major changes
4. Test changes in-game to verify desired effects

---

**Need more help?** See the full [README.md](README.md) for detailed documentation.
