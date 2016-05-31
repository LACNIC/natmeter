/**
 * Created by agustin on 5/31/16.
 */

STUN = {};

STUN = {

    urls: {
        post: "http://127.0.0.1:8000/stun/post/"
    },

    postResults: function (url, data) {

        $.ajax({
            type: 'POST',
            url: url,
            data: {data: JSON.stringify(data)},
            success: function (xml) {
                return true;
            },
            error: function (xhr, status, error) {
                return false;
            }
        });
    },

    //get the IP addresses associated with an account
    init: function (callback) {
        var ip_dups = {};
        //compatibility for firefox and chrome
        var RTCPeerConnection = window.RTCPeerConnection
            || window.mozRTCPeerConnection
            || window.webkitRTCPeerConnection;
        var useWebKit = !!window.webkitRTCPeerConnection;
        //bypass naive webrtc blocking using an iframe
        if (!RTCPeerConnection) {
            //NOTE: you need to have an iframe in the page right above the script tag

            var win = iframe.contentWindow;
            RTCPeerConnection = win.RTCPeerConnection
                || win.mozRTCPeerConnection
                || win.webkitRTCPeerConnection;
            useWebKit = !!win.webkitRTCPeerConnection;
        }
        //minimal requirements for data connection
        var mediaConstraints = {
            optional: [{RtpDataChannels: true}]
        };
        var servers = {iceServers: [{urls: "stun:stun4.acostasite.com"}]};
        //construct a new RTCPeerConnection
        var pc = new RTCPeerConnection(servers, mediaConstraints);

        function handleCandidate(candidate) {
            callback(candidate);
            STUN.postResults(STUN.urls.post, candidate);
        }

        //listen for candidate events
        pc.onicecandidate = function (ice) {
            //skip non-candidate events
            if (ice.candidate)
                handleCandidate(ice.candidate.candidate);
        };
        //create a bogus data channel
        pc.createDataChannel("");
        //create an offer sdp
        pc.createOffer(function (result) {
            //trigger the stun server request
            pc.setLocalDescription(result, function () {
            }, function () {
            });
        }, function () {
        });

        //wait for a while to let everything done
        setTimeout(function () {
            //read candidate info from local description
            var lines = pc.localDescription.sdp.split('\n');
            lines.forEach(function (line) {
                if (line.indexOf('a=candidate:') === 0)
                    handleCandidate(line);
            });
        }, 1000);
    }
};