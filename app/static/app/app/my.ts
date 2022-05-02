import document from "document";
import { HeartRateSensor } from "heart-rate"; 

// Fetch UI elements we will need to change
let hrtag = document.getElementById("hrm");
let updatedtag = document.getElementById("updated");
let hrmdiv = document.getElementById("hrmtext");

// Keep a timestamp of the last reading received. Start when the app is started.
let lastValueTimestamp = Date.now();

// Initialize the UI with some values
if(hrtag != undefined && updatedtag != undefined){
  hrtag.text = "--";
  updatedtag.text = "...";
}
// This function takes a number of milliseconds and returns a string
// such as "5min ago".
function convertMsAgoToString(millisecondsAgo) {
  if (millisecondsAgo < 120*1000) {
    return Math.round(millisecondsAgo / 1000) + "s ago";
  }
  else if (millisecondsAgo < 60*60*1000) {
    return Math.round(millisecondsAgo / (60*1000)) + "min ago";
  }
  else {
    return Math.round(millisecondsAgo / (60*60*1000)) + "h ago"
  }
}

// This function updates the label on the display that shows when data was last updated.
function updateDisplay() {
  if (lastValueTimestamp !== undefined) {
    updatedtag.text = convertMsAgoToString(Date.now() - lastValueTimestamp);
  }
}

if(HeartRateSensor){
  let hrm = new HeartRateSensor();
  
  //Event handler that will be called every time a new HR value is received.
  hrm.onreading = function() {
    console.log("Current heart rate: " + hrm.heartRate);
    hrtag.text = hrm.heartRate.toString();
    hrmdiv.text = hrm.heartRate.toString();
    lastValueTimestamp = Date.now();
  }
  //Begin monitoring the sensor
  hrm.start();
  setInterval(updateDisplay, 1000);
}


