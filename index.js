var App = {};

var remote = require('electron').remote; 
var ipc = require('electron').ipcRenderer;


window.onload = function() {
  document.getElementById("p1").innerHTML = 'IB-TradeTron App';
}()


var dialog = remote.dialog; 
function openFile () {
  dialog.showOpenDialog(function (fileNames) {
      if (fileNames === undefined) return;
      App.fileName = fileNames[0];
      document.getElementById("tradeFile").innerHTML = App.fileName;
  });
}

function uploadFiles() {
  ipc.send('log');

  if (App.fileName == undefined) return;
  ipc.send('upload', App.fileName);
}

ipc.on('info' , function(event , data) { 
    document.getElementById("log").innerHTML = data;
});
