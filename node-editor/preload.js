const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  selectFolderDocs: () => ipcRenderer.invoke('select-folder-docs'),
  scanIniFiles: (rootPath, exclusions) => ipcRenderer.invoke('scan-ini-files', rootPath, exclusions),
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, contents) => ipcRenderer.invoke('write-file', filePath, contents),
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
});
