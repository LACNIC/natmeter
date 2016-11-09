/**
 * Created by agustin on 5/31/16.
 */

STUN = {};
STUN.debug = false;
STUN = {

    urls: {
        post: STUN.debug && "http://127.0.0.1:8000/post/" || "https://natmeter.labs.lacnic.net/post/"
    },

    callbacks: {

        before_cookie: function () {

        },
        after_cookie: function () {

        },
        before_private_request: function () {

        },
        after_private_request: function () {

        },
        after_private_stun_response: function(candidate) {

        },
        before_public_request: function () {

        },
        after_public_request: function () {

        },
        after_public_stun_response: function(candidate) {

        },
        before_stun_response: function () {

        },
        after_stun_response: function (line) {

        },
        before_post: function () {

        },
        after_post: function () {

        },
        error_post: function () {

        },
        after_experiment: function () {

        }
    },

    iceServers: [],

    COOKIES: {

        cookieName: "lacnic-stun-cookie",
        cookieDays: 14,

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
            STUN.COOKIES.createCookie(name, "", -1);
        },

        createSTUNCookie: function (cookieValue) {
            return this.createCookie(this.cookieName, cookieValue, this.cookieDays);
        },

        readSTUNCookie: function () {
            return this.readCookie(this.cookieName);
        }
    },

    NETWORK: {
        CONSTANTS: {
            v4: 4,
            v6: 6
        },
        addresses: { // IP addresses as seen externally
            private: [],
            public: [],
            getPrivateAddresses: function () {
                return STUN.NETWORK.addresses.private;
            },
            getPublicAddresses: function () {
                return STUN.NETWORK.addresses.public;
            }
        },
        ip_address_change_event: {
            previous: "",
            current: ""
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

        STUN.callbacks.before_post();

        const experimentId = STUN.getExperimentId();
        const cookie = STUN.COOKIES.readCookie(STUN.COOKIES.cookieName);
        const data = {
            experiment_id: experimentId,
            cookie: cookie,
            addresses: JSON.stringify(STUN.NETWORK.addresses),
            ip_address_change_event: JSON.stringify(STUN.NETWORK.ip_address_change_event),
            date: new Date(),
            tester_version: 1
        };

        $.ajax({
            type: 'POST',
            url: STUN.urls.post,
            data: data,
            success: function (xml) {
                if (xml == "OK") {
                    STUN.callbacks.after_post();
                    return true;
                }
                return false;
            },
            error: function (xhr, status, error) {
                STUN.callbacks.error_post();
                return false;
            }
        });
    },

    //get the IP addresses associated with an account
    _init: function () {

        const experimentId = STUN.getExperimentId();
        STUN.experimentId = experimentId;
        STUN.callbacks.before_cookie();
        if (STUN.COOKIES.readSTUNCookie() == null) {
            STUN.COOKIES.createSTUNCookie(experimentId);
        }
        STUN.callbacks.after_cookie();

        STUN.callbacks.before_stun_response();

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

        //construct a new RTCPeerConnection
        var pc = new RTCPeerConnection({iceServers: STUN.iceServers}, mediaConstraints);

        function handleCandidate(candidate) {
            STUN.callbacks.after_stun_response(candidate);
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

            STUN.callbacks.after_experiment();

        }, 8000);
    },

    init: function () {
        /*
         * First run trying the local connection
         */
        STUN.callbacks.after_stun_response = function (response) {

            STUN.callbacks.after_private_stun_response(response);

            var address = response.split(" ")[4];
            if (STUN.NETWORK.addresses.private.indexOf(address) <= -1) {
                STUN.NETWORK.addresses.private.push(address);
            }
        }

        STUN.callbacks.after_experiment = function () {
            setTimeout(function () {

                /*
                 * Second run trying the remote connection (after 2 seconds...)
                 */
                STUN.callbacks.after_stun_response = function (response) {

                    STUN.callbacks.after_public_stun_response(response);

                    var address = response.split(" ")[4];
                    if (STUN.NETWORK.addresses.public.indexOf(address) <= -1 && STUN.NETWORK.addresses.private.indexOf(address) <= -1) {
                        STUN.NETWORK.addresses.public.push(address);
                    }

                    return true;
                }

                STUN.callbacks.after_experiment = function () {
                    STUN.postResults();
                }

                STUN.callbacks.before_public_request();
                STUN.iceServers = [
                    {
                        urls: ["stun:stun4.acostasite.com", "stun:stun6.acostasite.com"]
                    }
                ];
                STUN._init();
                STUN.callbacks.after_public_request();

            }, 2000);
        }

        STUN.callbacks.before_private_request();
        STUN.iceServers = [];
        STUN._init();
        STUN.callbacks.after_private_request();
    },

    PARAMS: {
        validate: function (param) {
            return param != null && param != undefined;
        }
    },

    console: {
        HEADER: "[STUN] : ",
        TRAILER: " (" + new Date() + ")",
        log: function (txt) {
            console.log(this.HEADER + txt + this.TRAILER);
        }
    }
};