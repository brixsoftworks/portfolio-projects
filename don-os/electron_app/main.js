const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

// Linux container compatibility; keep Chromium's automatic GPU acceleration enabled for video playback.
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-dev-shm-usage');


let mainWindow;


let pythonProcess = null;
const BACKEND_PORT = 8765;

function checkBackendHealth(retries = 15, delay = 600) {
  return new Promise((resolve) => {
    const attempt = (remaining) => {
      const req = http.get(`http://127.0.0.1:${BACKEND_PORT}/api/health`, (res) => {
        if (res.statusCode === 200) {
          resolve(true);
        } else if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delay);
        } else {
          resolve(false);
        }
      });
      req.on('error', () => {
        if (remaining > 0) {
          setTimeout(() => attempt(remaining - 1), delay);
        } else {
          resolve(false);
        }
      });
      req.end();
    };
    attempt(retries);
  });
}

function startBackendServer() {
  const projectRoot = path.join(__dirname, '..');
  const pythonBin = '/usr/bin/python3';
  const serverScript = path.join(projectRoot, 'agent_server.py');

  pythonProcess = spawn(pythonBin, [serverScript], {
    cwd: projectRoot,
    stdio: 'inherit'
  });

  pythonProcess.on('error', (err) => {
    console.error('Failed to spawn Python backend:', err);
  });
}

async function createWindow() {
  // Check if server is already running, if not spawn it
  const isHealthy = await checkBackendHealth(2, 300);
  if (!isHealthy) {
    console.log('Starting Python agent backend server...');
    startBackendServer();
    await checkBackendHealth(20, 500);
  }

  // Auto-grant media/microphone permissions for voice recognition
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(true);
  });

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 820,
    minWidth: 800,
    minHeight: 580,
    title: 'DON OS - Workstation AI',
    icon: path.join(__dirname, 'icon.png'),
    backgroundColor: '#0c0f1d',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  mainWindow.webContents.on('dom-ready', () => {
    console.log('[DON OS]: DOM successfully loaded and ready.');
  });

  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[Renderer Console]: ${message}`);
  });

  mainWindow.webContents.on('did-fail-load', (e, errorCode, errorDescription) => {
    console.error(`[Load Error ${errorCode}]: ${errorDescription}`);
  });

  mainWindow.webContents.on('render-process-gone', (e, details) => {
    console.error(`[Renderer Gone]: ${JSON.stringify(details)}`);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  if (pythonProcess) {
    pythonProcess.kill('SIGTERM');
  }
});
