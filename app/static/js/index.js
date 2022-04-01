let document = require("document");
import { HeartRateSensor } from "heart-rate";

let hrtag = document.getElementById("hrm");
let updated = document.getElementById("updated");
let Timestamp = Date.now();
let interval = null;
hrtag = "---";
updated = "...";

//for converting milliseconds to string;
function MsToString(milliseconds) {
    if (milliseconds < 120*1000) {
      return Math.round(milliseconds / 1000) + "s ago";
    }
    else if (milliseconds < 60*60*1000) {
      return Math.round(milliseconds / (60*1000)) + "min ago";
    }
    else {
      return Math.round(milliseconds / (60*60*1000)) + "h ago"
    }
}

function updateDisplay() {
    if (Timestamp !== undefined) {
        updated.text = MsToString(Date.now() - Timestamp);
    }
}

var hrm = new HeartRateSensor();

// Declare an event handler that will be called every time a new HR value is received.
hrm.onreading = function() {
  // Peek the current sensor values
  console.log("Current heart rate: " + hrm.heartRate);
  hrtag.text = hrm.heartRate;
  Timestamp = Date.now();
}


function hrmeter(){
  hrm.start();
  interval = setInterval(updateDisplay, 1000);
}

function stophrmeter(){
  hrm.stop();
  clearInterval(interval);
}

console.log("App code started");
