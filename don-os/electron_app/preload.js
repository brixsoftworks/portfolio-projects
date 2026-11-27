const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('api', {
  backendUrl: 'http://127.0.0.1:8765'
});

