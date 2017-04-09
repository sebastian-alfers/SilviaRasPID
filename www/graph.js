function init() {
  initHost('host1');
}

var seriesOptions = [
    { strokeStyle: 'rgba(255, 0, 0, 1)', fillStyle: 'rgba(255, 0, 0, 0.1)', lineWidth: 3 },
    { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.1)', lineWidth: 3 }
  ];

function initHost(hostId) {

  // Initialize an empty TimeSeries for each CPU.
  var tempDataSets = [new TimeSeries(),new TimeSeries()];

  // Every second, simulate a new set of readings being taken from each CPU.
  setInterval(function() {

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var json = JSON.parse(xmlHttp.responseText)
            var dateTime = new Date().getTime()
            tempDataSets[0].append(dateTime, json.avgTemp);
            tempDataSets[1].append(dateTime, json.avgPid);
            document.getElementById("curr_temp").innerHTML = json.avgTemp;
            document.getElementById("curr_pid").innerHTML = json.avgPid;
            document.getElementById("heatStatus").innerHTML = json.isHeating;
        }
    }
    xmlHttp.open("GET", "/temp", true); // true for asynchronous
    xmlHttp.send(null);
  }, 1000);

  //, maxValue:170,minValue:80,

  // Build the timeline
  var timeline = new SmoothieChart({ millisPerPixel: 20, grid: { strokeStyle: 'transparent', lineWidth: 1, millisPerLine: 1000, verticalSections: 4 },  millisPerPixel: 1500});
  timeline.addTimeSeries(tempDataSets[0], seriesOptions[0]);
  timeline.addTimeSeries(tempDataSets[1], seriesOptions[1]);
  timeline.streamTo(document.getElementById(hostId + 'Cpu'), 1000);
}