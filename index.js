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
  
  var ul = document.getElementById("resultsLog");

  
  var log_list = data.split("SPLIT")[1].split("\n");

  for (i=0; i < log_list.length; i++) {
    var text = log_list[i];
    if (text.length == 0) continue

    var li = document.createElement("li");
    li.appendChild(document.createTextNode(text));
    ul.appendChild(li);
  }
});

