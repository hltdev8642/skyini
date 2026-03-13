const el = (id) => document.getElementById(id);

const state = {
  gamePath: null,
  docsPath: null,
  scanRoot: null,
  iniFiles: [],
  filteredFiles: [],
  currentFile: null,
  exclusions: [],
  rawView: false,
  viewMode: 'tree',
};

function setStatus(message) {
  el('status').textContent = message;
}

async function loadSettings() {
  const settings = await window.electronAPI.getSettings();
  if (!settings) return;

  if (settings.gamePath) state.gamePath = settings.gamePath;
  if (settings.docsPath) state.docsPath = settings.docsPath;
  if (Array.isArray(settings.exclusions)) state.exclusions = settings.exclusions;
  if (settings.viewMode) state.viewMode = settings.viewMode;
  if (settings.lastFile) state.currentFile = settings.lastFile;

  if (state.exclusions.length) updateExcludeList();
  updateFileViewButton();

  if (state.gamePath || state.docsPath) {
    await rescan();
    if (state.currentFile) {
      // Try to restore the last opened file if it still exists
      const exists = state.iniFiles.includes(state.currentFile);
      if (exists) {
        await loadFile(state.currentFile);
      }
    }
  }
}

function saveSettings() {
  const settings = {
    gamePath: state.gamePath,
    docsPath: state.docsPath,
    exclusions: state.exclusions,
    viewMode: state.viewMode,
    lastFile: state.currentFile,
  };
  window.electronAPI.saveSettings(settings);
}

function setButtonEnabled(id, enabled) {
  const btn = el(id);
  if (!btn) return;
  btn.disabled = !enabled;
}

function getRelativePath(filePath) {
  if (!state.scanRoot) return filePath;

  const normalize = (p) => p.replace(/\//g, '\\').replace(/\\+/, '\\').replace(/\s+$/, '');
  const root = normalize(state.scanRoot);
  const target = normalize(filePath);

  if (!target.startsWith(root)) return filePath;

  const rel = target.slice(root.length);
  return rel.startsWith('\\') ? rel.slice(1) : rel;
}

function shortenPath(relPath, maxLen = 60) {
  if (!relPath) return relPath;
  if (relPath.length <= maxLen) return relPath;

  const parts = relPath.split(/[\\/]/).filter(Boolean);
  if (parts.length <= 2) {
    return relPath.slice(-maxLen);
  }

  const tail = parts.slice(-2).join('\\');
  return `...\\${tail}`;
}

function buildFileList(files) {
  const list = el('fileList');
  list.innerHTML = '';

  if (state.viewMode === 'tree') {
    buildTreeView(files, list);
  } else {
    buildFlatView(files, list);
  }
}

function buildFlatView(files, list) {
  files.forEach((file) => {
    const rel = getRelativePath(file);
    const li = document.createElement('li');
    li.textContent = shortenPath(rel);
    li.title = rel;
    li.dataset.filePath = file;
    li.addEventListener('click', () => loadFile(file));
    if (file === state.currentFile) li.classList.add('selected');
    list.appendChild(li);
  });
}

function buildTreeView(files, list) {
  const tree = {};

  files.forEach((file) => {
    const rel = getRelativePath(file);
    const parts = rel.split(/[\\/]/).filter((p) => p);
    let node = tree;

    parts.forEach((part, index) => {
      if (index === parts.length - 1) {
        node[part] = file;
      } else {
        node[part] = node[part] || {};
        node = node[part];
      }
    });
  });

  function renderNode(node, parent) {
    const entries = Object.keys(node).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
    entries.forEach((key) => {
      const value = node[key];
      if (typeof value === 'string') {
        const li = document.createElement('li');
        li.textContent = key;
        li.title = getRelativePath(value);
        li.dataset.filePath = value;
        li.addEventListener('click', () => loadFile(value));
        if (value === state.currentFile) li.classList.add('selected');
        parent.appendChild(li);
      } else {
        const details = document.createElement('details');
        const summary = document.createElement('summary');
        summary.textContent = key;
        details.appendChild(summary);
        const nested = document.createElement('ul');
        nested.className = 'file-list nested';
        renderNode(value, nested);
        details.appendChild(nested);
        const li = document.createElement('li');
        li.appendChild(details);
        parent.appendChild(li);
      }
    });
  }

  renderNode(tree, list);
}

function filterFiles() {
  const query = el('filter').value.trim().toLowerCase();
  if (!query) {
    state.filteredFiles = [...state.iniFiles];
  } else {
    state.filteredFiles = state.iniFiles.filter((f) => {
      const rel = getRelativePath(f).toLowerCase();
      return f.toLowerCase().includes(query) || rel.includes(query);
    });
  }
  buildFileList(state.filteredFiles);
}

function updateExcludeList() {
  const list = el('excludeList');
  list.innerHTML = '';
  state.exclusions.forEach((ex, idx) => {
    const li = document.createElement('li');
    li.textContent = ex;
    const remove = document.createElement('button');
    remove.textContent = '✕';
    remove.addEventListener('click', () => {
      state.exclusions.splice(idx, 1);
      updateExcludeList();
      rescan();
    });
    li.appendChild(remove);
    list.appendChild(li);
  });
}

async function rescan() {
  if (!state.gamePath && !state.docsPath) {
    setStatus('Select a Skyrim folder or Documents folder to scan.');
    return;
  }

  setStatus('Scanning for INI files...');
  const root = state.gamePath || state.docsPath;
  state.scanRoot = root;
  const { files, error } = await window.electronAPI.scanIniFiles(root, state.exclusions);
  if (error) {
    setStatus('Scan failed: ' + error);
    return;
  }

  state.iniFiles = files.sort();
  filterFiles();
  setStatus(`Found ${files.length} .ini files`);
  setButtonEnabled('btnSave', !!state.currentFile);
  setButtonEnabled('btnToggleView', !!state.currentFile);
  setButtonEnabled('btnToggleFileView', state.iniFiles.length > 0);
  updateFileViewButton();
  saveSettings();
}

async function loadFile(filePath) {
  state.currentFile = filePath;
  setStatus('Loading ' + filePath);
  const contents = await window.electronAPI.readFile(filePath);

  const displayName = getRelativePath(filePath);
  el('currentFileName').textContent = displayName;
  el('currentFileName').title = filePath;
  el('rawText').value = contents;
  state.rawView = false;
  updateView();

  setButtonEnabled('btnSave', true);
  setButtonEnabled('btnToggleView', true);
  highlightSelectedFile();
  saveSettings();
}

function highlightSelectedFile() {
  const items = document.querySelectorAll('#fileList li');
  items.forEach((item) => {
    const itemPath = item.dataset.filePath;
    item.classList.toggle('selected', itemPath === state.currentFile);
  });
}

function toggleView() {
  state.rawView = !state.rawView;
  updateView();
}

function updateFileViewButton() {
  const btn = el('btnToggleFileView');
  if (!btn) return;
  if (state.viewMode === 'tree') {
    btn.textContent = 'Flat';
    btn.title = 'Switch to flat file list';
  } else {
    btn.textContent = 'Tree';
    btn.title = 'Switch to tree view';
  }
}

function toggleFileView() {
  state.viewMode = state.viewMode === 'tree' ? 'flat' : 'tree';
  updateFileViewButton();
  saveSettings();
  buildFileList(state.filteredFiles);
}

function updateView() {
  el('inspector').style.display = state.rawView ? 'none' : 'block';
  el('rawText').style.display = state.rawView ? 'block' : 'none';
  el('btnToggleView').textContent = state.rawView ? 'Toggle Properties' : 'Toggle Raw';

  if (!state.rawView) {
    renderInspector();
  }
}

function parseIniWithComments(raw) {
  const lines = raw.split(/\r?\n/);
  const sections = {};
  let currentSection = '';
  let pendingComments = [];

  function addProperty(key, value) {
    if (!sections[currentSection]) {
      sections[currentSection] = { properties: [], comments: [] };
    }

    sections[currentSection].properties.push({
      key,
      value,
      comments: pendingComments,
    });
    pendingComments = [];
  }

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith(';') || trimmed.startsWith('#') || trimmed === '') {
      pendingComments.push(line);
      return;
    }

    const sectionMatch = trimmed.match(/^\[([^\]]+)\]$/);
    if (sectionMatch) {
      currentSection = sectionMatch[1];
      if (!sections[currentSection]) {
        sections[currentSection] = { properties: [], comments: [] };
      }
      sections[currentSection].comments = (sections[currentSection].comments || []).concat(pendingComments);
      pendingComments = [];
      return;
    }

    const kv = line.split('=');
    if (kv.length >= 2) {
      const key = kv.shift().trim();
      const val = kv.join('=').trim();
      addProperty(key, val);
      return;
    }

    // Fallback: treat as comment
    pendingComments.push(line);
  });

  return sections;
}

function renderInspector() {
  const container = el('inspector');
  container.innerHTML = '';
  const raw = el('rawText').value;
  const sections = parseIniWithComments(raw);

  Object.keys(sections).forEach((section) => {
    const sectionDiv = document.createElement('div');
    sectionDiv.className = 'section';

    const header = document.createElement('h3');
    header.textContent = section || '(global)';
    sectionDiv.appendChild(header);

    const sectionComments = sections[section].comments || [];
    sectionComments.forEach((comment) => {
      const p = document.createElement('p');
      p.className = 'comment';
      p.textContent = comment;
      sectionDiv.appendChild(p);
    });

    sections[section].properties.forEach((prop) => {
      const propRow = document.createElement('div');
      propRow.className = 'prop-row';

      const label = document.createElement('label');
      label.textContent = prop.key;
      label.title = prop.key;

      const input = document.createElement('input');
      input.value = prop.value;
      input.addEventListener('input', () => {
        prop.value = input.value;
        rebuildRawFromInspector(sections);
      });

      propRow.appendChild(label);
      propRow.appendChild(input);

      if (prop.comments && prop.comments.length) {
        const commentDiv = document.createElement('div');
        commentDiv.className = 'prop-comments';
        prop.comments.forEach((comment) => {
          const p = document.createElement('p');
          p.textContent = comment;
          commentDiv.appendChild(p);
        });
        propRow.appendChild(commentDiv);
      }

      sectionDiv.appendChild(propRow);
    });

    container.appendChild(sectionDiv);
  });
}

function rebuildRawFromInspector(sections) {
  const lines = [];
  Object.keys(sections).forEach((section) => {
    const sectionData = sections[section];
    if (section !== '') {
      lines.push('[' + section + ']');
    }
    (sectionData.comments || []).forEach((comment) => lines.push(comment));
    sectionData.properties.forEach((prop) => {
      (prop.comments || []).forEach((comment) => lines.push(comment));
      lines.push(`${prop.key} = ${prop.value}`);
    });
    lines.push('');
  });

  el('rawText').value = lines.join('\n');
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[m]));
}

async function saveFile() {
  if (!state.currentFile) return;
  const contents = el('rawText').value;
  await window.electronAPI.writeFile(state.currentFile, contents);
  setStatus('Saved ' + state.currentFile);
}

function createInspectorStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .section { margin-bottom: 16px; }
    .section h3 { margin: 0 0 6px; font-size: 14px; color: #a8dcdc; }
    .comment { margin: 0 0 4px; font-size: 12px; color: rgba(255,255,255,0.65); }
    .prop-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px; }
    .prop-row label { flex: 0 0 220px; font-size: 13px; color: #cfd8dc; }
    .prop-row input { flex: 1 1 240px; padding: 6px 8px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e6e6e6; border-radius: 4px; }
    .prop-comments p { margin: 0; font-size: 12px; color: rgba(255,255,255,0.6); }
    .comment { color: rgba(255, 255, 255, 0.55); }
    .section { color: #7ab5ff; }
    .key { color: #ffcc66; }
    .value { color: #b5ffb5; }
  `;
  document.head.appendChild(style);
}

function bindEvents() {
  el('btnSelectGame').addEventListener('click', async () => {
    const folder = await window.electronAPI.selectFolder();
    if (!folder) return;
    state.gamePath = folder;
    setStatus('Selected game path: ' + folder);
    await rescan();
    saveSettings();
  });

  el('btnSelectDocs').addEventListener('click', async () => {
    const folder = await window.electronAPI.selectFolderDocs();
    if (!folder) return;
    state.docsPath = folder;
    setStatus('Selected documents path: ' + folder);
    await rescan();
    saveSettings();
  });

  el('btnRescan').addEventListener('click', rescan);
  el('btnSave').addEventListener('click', saveFile);
  el('btnToggleView').addEventListener('click', toggleView);
  el('btnToggleFileView').addEventListener('click', toggleFileView);
  el('btnClearFilter').addEventListener('click', () => {
    el('filter').value = '';
    filterFiles();
  });

  el('filter').addEventListener('input', filterFiles);
  el('excludeInput').addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
      el('btnAddExclude').click();
    }
  });
  el('btnAddExclude').addEventListener('click', () => {
    const value = el('excludeInput').value.trim();
    if (!value) return;
    if (!state.exclusions.includes(value)) {
      state.exclusions.push(value);
      updateExcludeList();
      rescan();
    }
    el('excludeInput').value = '';
  });
}

window.addEventListener('DOMContentLoaded', async () => {
  createInspectorStyles();
  bindEvents();
  setButtonEnabled('btnToggleFileView', false);
  updateFileViewButton();
  setStatus('Ready. Select a folder to begin.');
  await loadSettings();
});
