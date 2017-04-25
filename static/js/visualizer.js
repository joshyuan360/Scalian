/**
 * Joshua Yuan
 * June 2016
 * Audio visualizer using Web Audio API (AnalyserNode).
 * Bar heights and cloud opacity are adjusted based on real-time frequency analysis data.
 * CSS animations are controlled using JQuery.
 */

$(document).ready(function() {
    // Creates a new AudioContext object.
    var context;
    if (typeof AudioContext !== "undefined") {
        context = new AudioContext();
    } else if (typeof webkitAudioContext !== "undefined") {
        context = new webkitAudioContext();
    } else {
        return;
    }

    // Creates a new AnalyserNode with a Fast Fourier Transform size of 2048,
    // which represents the frequency domain.
    var analyser = context.createAnalyser();
    var cut = 370;                               // remove inaudible high frequencies

    analyser.fftSize = 2048;                     // max precision necessary for bass bars (similar frequencies)
    analyser.smoothingTimeConstant = 0.6;        // less smooth but more responsive than default 0.8
    analyser.maxDecibels = -10;                  // higher max prevents bars from reaching limit too often

    // Determines the frequencies displayed by graphic equalizer.
    var targetFrequencies = [63, 125, 200, 250, 315, 400, 500, 630, 800,
    1000, 1200, 1600, 2000, 2500, 3100, 4000, 5000, 6300, 8000, 10000, 12000, 16000, 20000];

    var frequencyData = new Uint8Array(analyser.frequencyBinCount); // raw data from analysernode
    var displayData = new Array();                                   // final heights to be used for the bars
    var freqIndex = new Array();                                     // displayData [i] = frequencyData [freqIndex [i]]
    var freqBand = 44100 / (analyser.fftSize / 2 - cut);             // frequency band of analysernode data

    for (var i = 0; i < targetFrequencies.length; i++) {
        freqIndex[i] = Math.round(targetFrequencies [i] / freqBand);
    }

    // Adds new div elements to the visualisation element, and sets the left position of each.
    var barSpacingPercent = 100 / (targetFrequencies.length);
    // uncomment more colours if necessary
    var barColors = [ '#02e300', /*'#03da26',*/ '#00e24d', /*'#01d86c',*/
                      '#01d993', /*'#048571',*/ '#07dcde', /*'#01afda',*/
                      '#0194e3', /*'#0073e3',*/ '#0448da', /*'#0025e2',*/
                      '#0301ba', /*'#2600dc',*/ '#4403dc', /*'#6e01da',*/
                      '#9500e0', /*'#bc00d8',*/ '#bd00da', /*'#dc00df',*/
                      '#8a017c', /*'#b1026d',*/ '#dd006e', /*'#910434',*/
                      '#dc022c', /*'#d90201',*/ '#de2600', /*'#df4a05',*/
                      '#c76200', '#e39601', '#e6be00', '#d8df06',
                      '#ddde02', '#bee400', '#90d404', '#72db00',
                      '#4ce400', '#24e402', '#01e309', '#01dd25'];

    // Adds a series of bars to the visualisation element.
    for (var i = 0; i < targetFrequencies.length; i++) {
        var $tempBar = $('<div/>');

        $tempBar.css("left", i * barSpacingPercent + "%");
        $tempBar.css("background", 'linear-gradient(white, ' + barColors[i] + ')');
        // $tempBar.css ("background", 'linear-gradient(' + barColors [i] + ', white, ' + barColors [i] + ')');

        $tempBar.attr("class", "bar");

        $(visualisation).append($tempBar);
    }

    // Adds a series of lines to each bar.
    var bars = $("#visualisation > div");
    // bars.each(function (index, bar) {
    //     for (var bottom = 20; bottom < 255; bottom += 25) {
    //         var $tempLine = $('<div/>');

    //         $tempLine.css("position", "absolute").css("background", "black");
    //         $tempLine.css("width", "100%").css("height", "5px");
    //         $tempLine.css("bottom", bottom + 'px');

    //         $(bar).append($tempLine);
    //     }
    // });

    // Attaches an event listener to the audio element.
    // When the player is ready to play, an audio source is created and attached to the analyser.
    // The analyser is then connected to the destination (speakers).
    var hello = true;
    $("#player").bind('canplay', function () {
        if (hello) {
            var source = context.createMediaElementSource(this);

            source.connect(analyser);
            analyser.connect(context.destination);
            hello = false;
        }
    });

    function update() {
        requestAnimationFrame(update);

        // Continuously fetches frequency data from the AnalyserNode.
        analyser.getByteFrequencyData(frequencyData);

        for (var i = 0; i < targetFrequencies.length; i++) {
            displayData[i] = frequencyData[freqIndex[i]];
        }

        // 1.5 exponent used for more dramatic visualizations.
        bars.each(function (index, bar) {
            var height = parseInt(Math.pow(displayData[index], 1.5) / 15);
            bar.style.height = height + 'px';
        });

        var lines = $(".bar > div");
        lines.each(function (index, line) {
            if ($(line).position().top < 0) {
                $(line).css("opacity", "0.0");
            } else {
                $(line).css("opacity", "0.8");
            }
        });


        // Cloud opacity calculated based on average frequency.
        var opacity = 0;
        for (var i = 0; i < targetFrequencies.length; i++) {
            opacity += displayData[i];
        }

        opacity /= targetFrequencies.length;
        $(".clouds").css("opacity", opacity / 255);

    };

    update();
});
