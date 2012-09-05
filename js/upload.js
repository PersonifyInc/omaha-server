//   This file is part of omaha-server.

//   omaha-server is free software: you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation, either version 3 of the License, or
//   (at your option) any later version.

//   omaha-server is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public License
//   along with omaha-server.  If not, see <http://www.gnu.org/licenses/>.

  var bytesUploaded = 0;
  var bytesTotal = 0;
  var previousBytesLoaded = 0;
  var intervalTimer = 0;

  function fileSelected() {
    var file = document.getElementById('fileToUpload').files[0];
    var fileSize = 0;
    if (file.size > 1024 * 1024)
      fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
    else
      fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('fileName').innerHTML = 'Name: ' + file.name;
    document.getElementById('fileSize').innerHTML = 'Size: ' + fileSize;
    document.getElementById('fileType').innerHTML = 'Type: ' + file.type;
  }

  function uploadFile() {
    previousBytesLoaded = 0;
    document.getElementById('uploadResponse').style.display = 'none';
    document.getElementById('progressNumber').innerHTML = '';
    var progressBar = document.getElementById('progressBar');
    progressBar.style.display = 'block';
    progressBar.style.width = '0px';

    /* If you want to upload only a file along with arbitary data that
       is not in the form, use this */
//    var fd = new FormData();
//    fd.append("author", "Shiv Kumar");
//    fd.append("name", "Html 5 File API/FormData");
//    fd.append("fileToUpload", document.getElementById('fileToUpload').files[0]);

    /* If you want to simply post the entire form, use this */
    //var fd = document.getElementById('form1').getFormData();
    var fd = new FormData();
    if (document.getElementById('newVersion')) {
      fd.append("newVersion", document.getElementById('newVersion').value);
    }
    if (document.getElementById('fromVersion')) {
      fd.append("fromVersion", document.getElementById('fromVersion').value);
    }
    if (document.getElementById('release_notes_text')) {
      fd.append("releaseNotes", document.getElementById('release_notes_text').value)
    }
    fd.append("fileToUpload", document.getElementById('fileToUpload').files[0]);

    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.addEventListener("error", uploadFailed, false);
    xhr.addEventListener("abort", uploadCanceled, false);
    xhr.open("POST", uploadPath);
    xhr.send(fd);

    intervalTimer = setInterval(updateTransferSpeed, 500);
  }

  function updateTransferSpeed() {
    var currentBytes = bytesUploaded;
    var bytesDiff = currentBytes - previousBytesLoaded;
    if (bytesDiff == 0) return;
    previousBytesLoaded = currentBytes;
    bytesDiff = bytesDiff * 2;
    var bytesRemaining = bytesTotal - previousBytesLoaded;
    var secondsRemaining = bytesRemaining / bytesDiff;

    var speed = "";
    if (bytesDiff > 1024 * 1024)
      speed = (Math.round(bytesDiff * 100/(1024*1024))/100).toString() + 'MBps';
    else if (bytesDiff > 1024)
      speed =  (Math.round(bytesDiff * 100/1024)/100).toString() + 'KBps';
    else
      speed = bytesDiff.toString() + 'Bps';
    document.getElementById('transferSpeedInfo').innerHTML = speed;
    document.getElementById('timeRemainingInfo').innerHTML = '| ' + secondsToString(secondsRemaining);
  }

  function secondsToString(seconds) {
    var h = Math.floor(seconds / 3600);
    var m = Math.floor(seconds % 3600 / 60);
    var s = Math.floor(seconds % 3600 % 60);
    return ((h > 0 ? h + ":" : "") + (m > 0 ? (h > 0 && m < 10 ? "0" : "") + m + ":" : "0:") + (s < 10 ? "0" : "") + s);
  }

  function uploadProgress(evt) {
    if (evt.lengthComputable) {
      bytesUploaded = evt.loaded;
      bytesTotal = evt.total;
      var percentComplete = Math.round(evt.loaded * 100 / evt.total);
      var bytesTransfered = '';
      if (bytesUploaded > 1024*1024)
        bytesTransfered = (Math.round(bytesUploaded * 100/(1024*1024))/100).toString() + 'MB';
      else if (bytesUploaded > 1024)
        bytesTransfered = (Math.round(bytesUploaded * 100/1024)/100).toString() + 'KB';
      else
        bytesTransfered = (Math.round(bytesUploaded * 100)/100).toString() + 'Bytes';

      document.getElementById('progressNumber').innerHTML = percentComplete.toString() + '%';
      document.getElementById('progressBar').style.width = (percentComplete * 7.4).toString() + 'px';
      document.getElementById('transferBytesInfo').innerHTML = bytesTransfered;
      if (percentComplete == 100) {
        //document.getElementById('progressInfo').style.display = 'none';
        var uploadResponse = document.getElementById('uploadResponse');
        uploadResponse.innerHTML = '<span style="font-size: 18pt; font-weight: bold;">Please wait...</span>';
        uploadResponse.style.display = 'block';
      }
    }
    else {
      document.getElementById('progressBar').innerHTML = 'unable to compute';
    }
  }

  function uploadComplete(evt) {
    clearInterval(intervalTimer);
    var uploadResponse = document.getElementById('uploadResponse');
    uploadResponse.innerHTML = evt.target.responseText;
    uploadResponse.style.display = 'block';
  }

  function uploadFailed(evt) {
    clearInterval(intervalTimer);
    alert("An error occurred while uploading the file.");
  }  

  function uploadCanceled(evt) {
    clearInterval(intervalTimer);
    alert("The upload has been canceled by the user or the browser dropped the connection.");
  }
