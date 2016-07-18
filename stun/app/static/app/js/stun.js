/**
 * Created by agustin on 5/31/16.
 */

STUN = {};
STUN.debug = false;
STUN = {

    urls: {
        post: STUN.debug && "http://127.0.0.1:8000/post/" || "https://natmeter.labs.lacnic.net/post/"
    },

    results: [],

    COOKIES: {
        createCookie: function (name, value, days) {
            if (days) {
                var date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                var expires = "; expires=" + date.toGMTString();
            }
            else var expires = "";
            document.cookie = name + "=" + value + expires + "; path=/";
        },

        readCookie: function (name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(';');
            for (var i = 0; i < ca.length; i++) {
                var c = ca[i];
                while (c.charAt(0) == ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        },

        eraseCookie: function (name) {
            createCookie(name, "", -1);
        }
    },

    getExperimentId: function () {
        var experimentId = "", separator = "-";
        var N = 10, n = 1E6;
        while (N > 0) {

            var pos = Math.floor(Math.random() * n);
            experimentId += pos + separator;
            N--;
        }

        experimentId = experimentId.substring(0, experimentId.length - 1);
        return experimentId;
    },

    postResults: function () {

        $.ajax({
            type: 'POST',
            url: STUN.urls.post,
            data: {
                data: "[\"" + STUN.results.join("\",\"") + "\"]",
                experiment_id: STUN.getExperimentId(),
                tester_version: 1
            },
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

        STUN.experimentId = STUN.getExperimentId();

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
            var address = candidate.split(" ")[4];
            if (STUN.results.indexOf(address) <= -1) {
                STUN.results.push(address);
            }
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

            STUN.postResults();

        }, 1000);
    }
};