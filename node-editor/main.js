const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

function getSettingsPath() {
  return path.join(app.getPath('userData'), 'settings.json');
}

async function loadSettings() {
  const settingsPath = getSettingsPath();
  try {
    const raw = await fs.promises.readFile(settingsPath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    return {};
  }
}

async function saveSettings(settings) {
  const settingsPath = getSettingsPath();
  try {
    await fs.promises.writeFile(settingsPath, JSON.stringify(settings, null, 2), 'utf8');
    return true;
  } catch (err) {
    console.error('Failed to save settings', err);
    return false;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, 'index.html'));
  win.setMenuBarVisibility(true);
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('select-folder', async (event) => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory'],
    title: 'Select Skyrim folder (Data/..)',
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('select-folder-docs', async (event) => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory'],
    title: 'Select Documents folder (My Games/Skyrim Special Edition)',
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('read-file', async (event, filePath) => {
  return fs.promises.readFile(filePath, 'utf8');
});

ipcMain.handle('write-file', async (event, filePath, contents) => {
  await fs.promises.writeFile(filePath, contents, 'utf8');
  return true;
});

ipcMain.handle('scan-ini-files', async (event, rootPath, exclusions) => {
  const results = [];

  function isExcluded(name) {
    if (!exclusions || !Array.isArray(exclusions)) return false;
    return exclusions.some((pattern) => {
      const normalized = pattern.trim().toLowerCase();
      if (!normalized) return false;
      return name.toLowerCase().includes(normalized);
    });
  }

  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.ini')) {
        if (!isExcluded(entry.name) && !isExcluded(fullPath)) {
          results.push(fullPath);
        }
      }
    }
  }

  try {
    walk(rootPath);
  } catch (err) {
    return { error: err.message };
  }
  return { files: results };
});

ipcMain.handle('get-settings', async () => {
  return await loadSettings();
});

ipcMain.handle('save-settings', async (event, settings) => {
  return await saveSettings(settings);
});
