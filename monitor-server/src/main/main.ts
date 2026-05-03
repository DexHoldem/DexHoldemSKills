import { app, BrowserWindow, Menu, globalShortcut } from 'electron';
import { startServer } from './server';

let mainWindow: BrowserWindow | null = null;
let serverPort = 3000;

function createWindow(): void {
  const isMac = process.platform === 'darwin';

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: 'DexHoldem Monitor',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    backgroundColor: '#f0f4f8',
    ...(isMac
      ? { titleBarStyle: 'hiddenInset', trafficLightPosition: { x: 12, y: 12 } }
      : { frame: true }),
  });

  mainWindow.loadURL(`http://localhost:${serverPort}`);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  const menu = Menu.buildFromTemplate([
    {
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        {
          label: 'Always on Top',
          type: 'checkbox',
          checked: false,
          click: (menuItem) => {
            mainWindow?.setAlwaysOnTop(menuItem.checked);
          },
        },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);
}

function parseArgs(): { port: number; expDirs: string[] } {
  const args = process.argv.slice(app.isPackaged ? 1 : 2);
  let port = 3000;
  const expDirs: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--port' && args[i + 1]) {
      port = parseInt(args[++i], 10);
    } else if (args[i] === '--exp-dir' && args[i + 1]) {
      expDirs.push(args[++i]);
    }
  }

  return { port, expDirs };
}

app.whenReady().then(async () => {
  const { port, expDirs } = parseArgs();
  serverPort = port;

  await startServer(serverPort, expDirs);
  createWindow();

  globalShortcut.register('CommandOrControl+Shift+T', () => {
    mainWindow?.setAlwaysOnTop(!mainWindow.isAlwaysOnTop());
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});
