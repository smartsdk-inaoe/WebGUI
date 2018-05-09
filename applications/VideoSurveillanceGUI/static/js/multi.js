/*
 * File: multi.js
 *
 * This file manages the connection between the page and the kurento media server to stream multiple cameras.
 *
 * Autor: Marlon Garcia (Adapted from the original index.js in kurento examples)
 *
 * Project: SmartSDK-Security
 *
 * Institution: INAOE
 *
 *
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
	this.ws = new WebSocket(wsaddress),
	this.webRtcPeer = null,
        this.stream = false,
	this.container = document.getElementById(this.id),
	this.videourl = url,
	this.sendMessage = function (message) {
						var jsonMessage = JSON.stringify(message);
						//console.log('Sending message: ' + jsonMessage);
						try{
							this.ws.send(jsonMessage);
						}catch(error){
							console.error('('+this.name+') Error: '+error.message);
						}
					},
	this.close = function () {this.ws.close();}
}

/// @function multi.start
/// This function defines the message protocols that will be used by the webrtc peer,
/// it requests a stream of video from a specific camera which address is defined in the variable videourl
/// @param {Object} cam camera object
function start(cam) {
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
        	                case 'streamStatus':
                                                if(parsedMessage.status!='true'){
                                                    cam.stream = true;
                                                    //console.log('camera '+cam.id+': '+parsedMessage.status);
                                                    cam.container.style.background = '';
                                                    cam.container.poster = '../static/images/stream-error.png';
                                                }
                                                break;
				default:
                                                break;
			}
	}
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
        setTimeout(function(){getStream(cam)}, 10000);
}

function getStream(cam){
    if(!cam.stream){
        if(document.getElementById(cam.id).src!=""){
            stop(cam);
        }
        setTimeout(function(){start(cam)}, 2000);
    }
}

function stop(cam) {
    if (cam.webRtcPeer) {
        cam.webRtcPeer.dispose();
        cam.webRtcPeer = null;

        var message = {
            id : 'stop'
        }
        cam.sendMessage(message);
    }
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
