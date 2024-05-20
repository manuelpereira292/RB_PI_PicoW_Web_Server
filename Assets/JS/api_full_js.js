// setup gauges
var potOpts = {
    angle: -0.2, // The span of the gauge arc
    lineWidth: 0.2, // The line thickness
    radiusScale: 0.97, // Relative radius
    pointer: {
        length: 0.41, // // Relative to gauge radius
        strokeWidth: 0.082, // The thickness
        color: '#000000' // Fill color
    },
    limitMax: true,     // If false, max value increases automatically if value > maxValue
    limitMin: true,     // If true, the min value of the gauge will be fixed
    highDpiSupport: true,     // High resolution support
    staticLabels: {
        font: "10px sans-serif",  // Specifies font
        labels: [0, 20, 40, 60, 80, 100],  // Print labels at these values
        color: "#000000",  // Optional: Label text color
        fractionDigits: 0  // Optional: Numerical precision. 0=round off.
    },
    staticZones: [
        {strokeStyle: "#F03E3E", min: 0, max: 60, height: 1}, // Green
        {strokeStyle: "#FFDD00", min: 60, max: 80, height: 1.2}, // Yellow
        {strokeStyle: "#30B32D", min: 80, max: 100, height: 1.4},  // Red
    ],
    renderTicks: {
        divisions: 10,
        divWidth: 1.1,
        divLength: 0.7,
        divColor: "#333333",
        subDivisions: 5,
        subLength: 0.5,
        subWidth: 0.6,
        subColor: "#666666"
    },

};

// INTRODUZIR DADOS RESPEITAR ORDEM HTML
var target = document.getElementById('wordGauge');

var target = document.getElementById('vrValue');
var target = document.getElementById('Emoji_Power');
var target = document.getElementById('amValue');
var target = document.getElementById('Emoji_Ignition');
var target = document.getElementById('canhValue');
var target = document.getElementById('Emoji_CANh');
var target = document.getElementById('canlValue');
var target = document.getElementById('Emoji_CANl');
var target = document.getElementById('canValue');
var target = document.getElementById('Emoji_CAN');
var target = document.getElementById('gpsValue');
var target = document.getElementById('Emoji_GPS');
var target = document.getElementById('onewireValue');
var target = document.getElementById('Emoji_OneWire');
var target = document.getElementById('ds18x20Value');
var target = document.getElementById('Emoji_Temp');
var target = document.getElementById('brValue');
var target = document.getElementById('Emoji_Fuel');
var target = document.getElementById('ctValue');
var target = document.getElementById('Emoji_Door');
var target = document.getElementById('azValue');
var target = document.getElementById('Emoji_Panic');
var target = document.getElementById('rsValue');
var target = document.getElementById('Emoji_UDB');
var target = document.getElementById('Emoji_SI');
var target = document.getElementById('Emoji_Immo');
var target = document.getElementById('Emoji_BOut');
var target = document.getElementById('Emoji_BIn');

var target = document.getElementById('vbatValue');
var target = document.getElementById('temperatureValue');
var target = document.getElementById('timeValue');
var target = document.getElementById('potGauge');

var gauge = new Gauge(target).setOptions(potOpts);
gauge.maxValue = 100;
gauge.minValue = 0;
gauge.animationSpeed = 60;
gauge.set(0);

var tempOpts = {
    angle: 0, // The span of the gauge arc
    lineWidth: 0.2, // The line thickness
    radiusScale: 0.97, // Relative radius
    pointer: {
        length: 0.41, // // Relative to gauge radius
        strokeWidth: 0.082, // The thickness
        color: '#000000' // Fill color
    },
    limitMax: true,     // If false, max value increases automatically if value > maxValue
    limitMin: true,     // If true, the min value of the gauge will be fixed
    highDpiSupport: true,     // High resolution support
    staticLabels: {
        font: "10px sans-serif",  // Specifies font
        labels: [0, 5, 10, 15, 20, 25, 30, 35, 40],  // Print labels at these values
        color: "#000000",  // Optional: Label text color
        fractionDigits: 0  // Optional: Numerical precision. 0=round off.
    },
    staticZones: [
        {strokeStyle: "#0000a0", min: 0, max: 15, height: 1}, // blue
        {strokeStyle: "#30B32D", min: 15, max: 25, height: 1.4}, // Green
        {strokeStyle: "#F03E3E", min: 25, max: 40, height: 1},  // Red
    ],
    renderTicks: {
        divisions: 8,
        divWidth: 1.1,
        divLength: 0.7,
        divColor: "#333333",
        subDivisions: 5,
        subLength: 0.5,
        subWidth: 0.6,
        subColor: "#666666"
    },

};

var tempTarget = document.getElementById('tempGauge');
var tempGauge = new Gauge(tempTarget).setOptions(tempOpts);
tempGauge.maxValue = 40;
tempGauge.minValue = 0;
tempGauge.animationSpeed = 60;
tempGauge.set(0);

gatherDataAjaxRunning = false;

function gatherData(){
    // stop overlapping requests
    if(gatherDataAjaxRunning) return;

    gatherDataAjaxRunning = true;
    let postData = {
        "action": "readData"
    };
    $.post( "/api", postData, function( data ) {
        // handle word
        wordPercent = parseInt(parseInt(data.word_value));
        gauge.set(wordPercent);
        $('#wordValue').html(wordPercent);
        
        // INTRODUZIR DADOS RESPEITAR ORDEM HTML
        $('#vrValue').html(data.vrValue);
        $('#amValue').html(data.amValue);
        $('#canhValue').html(data.canhValue);
        $('#canlValue').html(data.canlValue);
        $('#canValue').html(data.canValue);
        $('#gpsValue').html(data.gpsValue);
        $('#onewireValue').html(data.onewireValue);
        $('#ds18x20Value').html(data.ds18x20Value);
        $('#brValue').html(data.brValue);
        $('#ctValue').html(data.ctValue);
        $('#azValue').html(data.azValue);
        $('#rsValue').html(data.rsValue);
        
        $('#vbatValue').html(data.vbatValue);
        $('#temperatureValue').html(data.temperatureValue);
        $('#timeValue').html(data.timeValue);
        
        // handle gauge
        potPercent = parseInt(parseInt(data.pot_value) * 100 / 40600);
        gauge.set(potPercent);
        $('#potValue').html(potPercent);
        $('#potValue').removeClass(["bg-success", "bg-warning", "bg-danger"]);
        if(potPercent <= 60) {
            $('#potValue').addClass("bg-danger");
        }
        else if(potPercent <= 80) {
            $('#potValue').addClass("bg-warning");
        }
        else {
            $('#potValue').addClass("bg-success");
        }

        // handle temp gauge
        temp = parseFloat(data.temp_value);
        tempGauge.set(temp);
        $('#tempValue').html(temp.toFixed(1));
        $('#tempValue').removeClass(["bg-success", "bg-warning", "bg-danger"]);
        if(temp <= 15) {
            $('#tempValue').addClass("bg-primary");
        }
        else if(temp <= 25) {
            $('#tempValue').addClass("bg-success");
        }
        else {
            $('#tempValue').addClass("bg-danger");
        }

        // allow next data gather call
        gatherDataAjaxRunning = false;

    });
}

function SetSwitch(value) {
    let postData = {
    "action": "SetSwitch",
    "value": value,
    };
    $.post( "/api", postData, function( data ) {
        console.log(data);
        $('#Emoji_Power').html(data.Emoji_Power);
        $('#Emoji_Ignition').html(data.Emoji_Ignition);
        $('#Emoji_CANh').html(data.Emoji_CANh);
        $('#Emoji_CANl').html(data.Emoji_CANl);
        $('#Emoji_CAN').html(data.Emoji_CAN);
        $('#Emoji_GPS').html(data.Emoji_GPS);
        $('#Emoji_OneWire').html(data.Emoji_OneWire);
        $('#Emoji_Temp').html(data.Emoji_Temp);
        $('#Emoji_Fuel').html(data.Emoji_Fuel);
        $('#Emoji_Door').html(data.Emoji_Door);
        $('#Emoji_Panic').html(data.Emoji_Panic);
        $('#Emoji_UDB').html(data.Emoji_UDB);
        $('#Emoji_SI').html(data.Emoji_SI);
        $('#Emoji_Immo').html(data.Emoji_Immo);
        $('#Emoji_BOut').html(data.Emoji_BOut);
        $('#Emoji_BIn').html(data.Emoji_BIn);
    });
}

var rgb_ajax_in_progress = false;

function set_rgb_colour(color) {
    console.log("set_rgb_colour")
    // do not start new request until previous finished
    if(rgb_ajax_in_progress) return;
    
    let postData = {
        "action": "setRgbColour",
        "color": color
    };
    
    rgb_ajax_in_progress = true;
    
    $.post( "/api", postData, function( data ) {
        console.log(data);
        
        rgb_ajax_in_progress = false // allow next call
    });
}

var dataTimer;
$( document ).ready(function() {
    set_rgb_colour(); // initialise rgb display
    dataTimer = setInterval(window.gatherData,500); // call data every 0.5 seconds
});