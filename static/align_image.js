/**
 * Created by mudies on 17/10/14.
 */

var socket = io.connect('/');

socket.on('connect', function(){
    socket.emit('connect')
});

function draw() {
    var img_canvas = document.getElementById('image');

    if (img_canvas.getContext) {
        var img_ctx = img_canvas.getContext('2d');
        var imageObj = new Image();

        imageObj.onload = function () {
            img_ctx.drawImage(imageObj, 0, 0, 981, 1043);
        };
        imageObj.src = "http://localhost:5000/image";
    }
}
$(function () {
    $('#container').highcharts({
        chart: {
            type: 'area',
            zoomType: 'xy'
        },
        title: {
            text: 'Histogram',
            x: -20 //center
        },
        xAxis: {
            title: 'pixel value'
        },
        yAxis: {
            title: {
                text: 'Number of pixels'
            },
            type: 'logarithmic',
            min: 1,
            plotLines: [{
                value: 1,
                width: 1,
                color: '#808080'
            }]
        }
    });
});