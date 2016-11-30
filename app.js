//http://www.reactnativeexpress.com/
//
// https://www.fyears.org/2015/06/electron-as-gui-of-python-apps.html
var electron = require('electron');

electron.app.on('ready', function () {
   // var subpy = require('child_process').spawn('python', ['./hello.py']);
   // var subpy = require('child_process').exec('python ./hello.py');

  var mainWindow = new electron.BrowserWindow({width: 600, height: 800});
   var subpy = require('child_process').exec('python ./hello.py', function(a,b,c) { 
     console.log(b) 
   })

  mainWindow.loadURL('file://' + __dirname + '/index.html');
})

