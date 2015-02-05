/**
 * Created by mudies on 17/10/14.
 */

         // the URL of the WAMP Router (Crossbar.io)

         var global_session;
         var wsuri;
         if (document.location.origin == "file://") {
            wsuri = "ws://127.0.0.1:8080/ws";

         } else {
            wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
                        document.location.host + "/ws";
         }


         // the WAMP connection to the Router
         
         var connection = new autobahn.Connection({
            url: wsuri,
            realm: "realm1"
         });

         // fired when connection is established and session attached

         connection.onopen = function (session, details) {
            global_session = session;
            console.log("Connected");

            // SUBSCRIBE to a topic and receive events

            function on_image (args) {
               var img_canvas = document.getElementById('image');

               if (img_canvas.getContext) {
                var img_ctx = img_canvas.getContext('2d');
                var imageObj = new Image();

                imageObj.onload = function () {
                    img_ctx.drawImage(imageObj, 0, 0, 981, 1043);
                };
                imageObj.src = 'data:image/png;base64,' + args[0]
            }

               console.log("image() event received");
            }

            session.subscribe('com.example.image', on_image).then(
               function (sub) {
                  console.log('subscribed to topic');
               },
               function (err) {
                  console.log('failed to subscribe to topic', err);
               }
            );
         };


         // fired when connection was lost (or could not be established)
         //
         connection.onclose = function (reason, details) {
            console.log("Connection lost: " + reason);
         };


         // now actually open the connection
         //
         connection.open();

         $(function(){
            $("#power").slider({
                min: 0.1,
                max: 1,
                step: 0.1,
                slide: function ( event, ui) {
                    global_session.publish('as.saxs.align.power',[ui.value])
                }
            })
         });





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