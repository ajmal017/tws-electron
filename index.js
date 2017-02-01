var App = {};

var remote = require('electron').remote; 
var ipc = require('electron').ipcRenderer;

var dialog = remote.dialog; 
function openFile () {
  dialog.showOpenDialog(function (fileNames) {
      if (fileNames === undefined) return;
      App.fileName = fileNames[0];
      document.getElementById("tradeFile").innerHTML = App.fileName;
  });
}

function uploadFiles() {
  if (App.fileName == undefined) return;
  ipc.send('upload', App.fileName);
}

ipc.on('log' , function(event , data) { 
  
  var ul = document.getElementById("log");
  var log_list = data.split('INFO:');

  for (i=0; i < log_list.length; i++) {
    var text = log_list[i];
    var li = document.createElement("li");
    li.appendChild(document.createTextNode(text));
    ul.appendChild(li);
  }
});

