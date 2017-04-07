function init() {
  initHost('host1');
}

var seriesOptions = [{ strokeStyle: 'rgba(255, 0, 0, 1)', fillStyle: 'rgba(255, 0, 0, 0.1)', lineWidth: 3 }, ];

function initHost(hostId) {

  // Initialize an empty TimeSeries for each CPU.
  var cpuDataSets = [new TimeSeries()];

  // Every second, simulate a new set of readings being taken from each CPU.
  setInterval(function() {

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            	if(!isNaN(xmlHttp.responseText)){

                	cpuDataSets[0].append(new Date().getTime(), xmlHttp.responseText);
	                console.log(xmlHttp.responseText);

		}
		//callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", "/temp", true); // true for asynchronous
    xmlHttp.send(null);

	//console.log('do get it');
	//addRandomValueToDataSets(new Date().getTime(), cpuDataSets);
  }, 1000);

  //, maxValue:170,minValue:80,

  // Build the timeline
  var timeline = new SmoothieChart({ millisPerPixel: 20, grid: { strokeStyle: 'transparent', lineWidth: 1, millisPerLine: 1000, verticalSections: 4 },  millisPerPixel: 1500, maxValue:120,minValue:80});
  timeline.addTimeSeries(cpuDataSets[0], seriesOptions[0]);
  timeline.streamTo(document.getElementById(hostId + 'Cpu'), 1000);
}