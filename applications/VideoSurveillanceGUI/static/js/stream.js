/// @file stream.js
/// @namespace stream
/// Kurento connection functions, modified from the original to stream one camera in the Map.


/*
 * (C) Copyright 2015 Kurento (http://kurento.org/)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

/// @var address Websocket address to access the server from other computers
//var address = 'wss://' + location.hostname + ':8443/player'; 
var address = 'wss://smartsdksecurity.duckdns.org:8443/player'; 

/// @function camera
/// Definition of camera data to connect and send to the server, each camera will have a websocket to exchange messages with the server.
/// @param {String} cname name (to display) of the camera
/// @param {String} czone zone (subtitle) of the camera
/// @param {String} cid id of container of the camera
/// @param {String} url connection url
/// @return Camera object
function camera(cname,czone,cid,url) {
	this.name = cname,
	this.zone = czone,
	this.id = cid,
	this.ws = new WebSocket(address),
	this.webRtcPeer = null,
	this.stream = false,
	this.retryID = null,
	this.container = null,
	this.videourl = url,
	this.sendMessage = function(message) {
						var jsonMessage = JSON.stringify(message);
						//console.log('Sending message: ' + jsonMessage);
						try{
							this.ws.send(jsonMessage);
						}catch(error){
							console.error('('+this.name+') Error: '+error.message);
						}
					},
	this.close = function() {this.ws.close();}
}

function open(cam) {
	if(cam.ws.readyState === cam.ws.OPEN){
		//console.log('Open');
		cam.ws.onmessage = function(message) {
				var parsedMessage = JSON.parse(message.data);
				//console.log('Received message('+cam.name+'):', parsedMessage);
				switch (parsedMessage.id) {
					case 'startResponse':
							//console.log('SDP answer received from server. Processing ...');
							cam.webRtcPeer.processAnswer(parsedMessage.sdpAnswer, function(error) {
								if (error)
									return console.error('SDP answer error ('+cam.name+'): '+error);
							});
							break;
					case 'error':
							console.error('('+cam.name+'): '+parsedMessage.message);
							break;
					case 'iceCandidate':
							cam.webRtcPeer.addIceCandidate(parsedMessage.candidate, function(error) {
								if (error)
									return console.log('Error adding candidate('+cam.name+'): ' + error);
							});
							break;
					case 'iceCandidate':
							break;
					case 'videoInfo':
							cam.stream = true;
							break;
					default:
							break;
				}
		}
		cam.container = document.getElementById(cam.id);
		start(cam);
	}else{
		setTimeout(function(){open(cam)}, 500);
	}
}

function start(cam) {
	showSpinner(cam.container);
	// Only video by default
	var userMediaConstraints = {
		audio : false,
		video : true
	}
	var options = {
		remoteVideo : cam.container,
		mediaConstraints : userMediaConstraints,
		onicecandidate : function (candidate) {
							//console.log('Local candidate' + JSON.stringify(candidate));
							var message = {
								id : 'onIceCandidate',
								candidate : candidate
							}
							cam.sendMessage(message);
						}
	}
	//console.info('User media constraints' + userMediaConstraints);
	cam.webRtcPeer = new kurentoUtils.WebRtcPeer.WebRtcPeerRecvonly(options,
			function(error) {
				if (error){
					return console.error('WebRtcPeer Error('+cam.name+'): '+error);
				}
				cam.webRtcPeer.generateOffer(function (error, offerSdp) {
					if (error)
						return console.error('Error generating the offer('+cam.name+')');
					//console.info('Invoking SDP offer callback function ' + location.host);
					var message = {
						id : 'start',
						sdpOffer : offerSdp,
						videourl : cam.videourl
					}
					cam.sendMessage(message);
				});
			});
	cam.retryID = setTimeout(function(){getStream(cam)}, 10000);
}

function getStream(cam){
	//console.log('getStream:'+cam.id);
    if(!cam.stream){
        if(cam.container && cam.container.src!=""){
            stop(cam);
        }
        cam.retryID = setTimeout(function(){start(cam)}, 2000);
    }
}

function stop(cam) {
	//console.log('stop');
    if (cam.webRtcPeer) {
        cam.webRtcPeer.dispose();
        cam.webRtcPeer = null;
        var message = {
            id : 'stop'
        }
        cam.sendMessage(message);
    }
	cam.stream = false;
	clearInterval(cam.retryID);
}

function showSpinner() {
	for (var i = 0; i < arguments.length; i++) {
		arguments[i].poster = '';
		arguments[i].style.background = "center transparent url('../static/images/spinner.gif') no-repeat";
	}
}

function hideSpinner() {
	for (var i = 0; i < arguments.length; i++) {
		arguments[i].src = '';
		arguments[i].poster = '../static/images/webrtc.png';
		arguments[i].style.background = '';
	}
}

/**
 * Lightbox utility (to display media pipeline image in a modal dialog)
 */
$(document).delegate('*[data-toggle="lightbox"]', 'click', function(event) {
	event.preventDefault();
	$(this).ekkoLightbox();
});
