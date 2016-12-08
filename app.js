//http://www.reactnativeexpress.com/
// https://www.fyears.org/2015/06/electron-as-gui-of-python-apps.html
// https://discuss.atom.io/t/ipc-send-from-main-process-to-renderer/16046/3

var electron = require('electron');
var ipc = electron.ipcMain;

electron.app.on('ready', function () {
  var mainWindow = new electron.BrowserWindow({width: 600, height: 800});
  mainWindow.loadURL('file://' + __dirname + '/index.html');
  

  
  ipc.on('upload', function(event, data) {
    console.log('Start Python...');
    var cmd = 'python ./populate_ib_trades.py -t ' + data
    var subpy = require('child_process').exec(cmd, function(error, stdout, sterr) { 
      console.log(stdout);
    })
  })
  ipc.on('log', function(event, data) {
    event.sender.send('info', 'HELLO');
  })

})
