$(document).ready(function(){
    let video = document.querySelector("#videoElement");
    let canvas = document.querySelector("#canvasElement");
    let ctx = canvas.getContext('2d');
  
    var localMediaStream = null;
  
    var socket = io.connect('https://uex-toolbox.herokuapp.com/experiments/6?new_exp_name=plpl&numb=2&number=1');
  
    function sendSnapshot() {
      if (!localMediaStream) {
        return;
      }
  
      ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);
  
      let dataURL = canvas.toDataURL('image/jpeg');
      socket.emit('input image', dataURL);
    }
  
    socket.on('connect', function() {
      console.log('Connected!');
    });
  
    var constraints = {
      video: {
        width: { min: 640 },
        height: { min: 480 }
      }
    };
  
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
      video.srcObject = stream;
      localMediaStream = stream;
  
      setInterval(function () {
        sendSnapshot();
      }, 50);
    }).catch(function(error) {
      console.log(error);
    });
  });