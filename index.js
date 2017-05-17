var App = {};

var remote = require('electron').remote; 
var ipc = require('electron').ipcRenderer;

var dialog = remote.dialog; 
function openFile(type) {
  dialog.showOpenDialog(function (fileNames) {
      if (fileNames === undefined) return;
      App.fileName = fileNames[0];

      if (type == 'trade') {
        App.tradeFile = fileNames[0];
        document.getElementById("tradeFile").innerHTML = App.tradeFile;
      } else {
        App.allocationFile = fileNames[0];
        document.getElementById("allocationFile").innerHTML = App.allocationFile;
      }
  });
}

function uploadFiles() {
  if (App.fileName == undefined) return;

  $('#uploadFiles').button('loading');
  ipc.send('upload', { 'tradeFile': App.tradeFile, 'allocationFile': App.allocationFile });
}

ipc.on('log' , function(event , data) { 
  $('#uploadFiles').button('reset');

  var ul = document.getElementById("resultsLog");
  var table = document.getElementById("resultsTable");

  var log_list = data.split("SPLIT")[1].split("\n");

  for (i=0; i < log_list.length; i++) {
    var text = log_list[i];
    if (text.length == 0) continue

    // populate table
    var tradeline = text.split('TRADELINE')
    if (tradeline.length > 1) {
      var line_info = tradeline[1].split(" | ");
      var action = line_info[1];
      var profile = line_info[3];
      var shares = line_info[2];
      var ticker = profile.split("_")[1];

      var tr = document.createElement("tr");
      [ticker, action, shares, profile].forEach(function(element) {
        var td = document.createElement("td");
        td.appendChild(document.createTextNode(element));
        tr.appendChild(td);
      })
      table.appendChild(tr);

    } else {
      var li = document.createElement("li");
      li.appendChild(document.createTextNode(text));
      ul.appendChild(li);
    }
  } // end for loop
});

