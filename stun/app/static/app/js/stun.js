/**
 * Created by agustin on 5/31/16.
 */

define(['jquery'], function (_$) {

    var stun = {};
    stun.debug = false;
    stun.version = 1;

    stun.urls = {
        post: stun.debug && "http://127.0.0.1:8000/post/" || "https://natmeter.labs.lacnic.net/post/"
    };

    stun.callbacks = {

        before_cookie: function () {

        },
        after_cookie: function () {

        },
        on_cookie_hit: function () {

        },
        before_private_request: function () {

        },
        after_private_request: function () {

        },
        after_private_stun_response: function (candidate) {

        },
        before_public_request: function () {

        },
        after_public_request: function () {

        },
        after_public_stun_response: function (candidate) {

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
    };

    stun.iceServers = [];

    stun.COOKIES = {

        cookieName: "lacnic-stun-cookie",
        cookieDays: 14,

        createCookie: function (name, value, days) {
            if (days) {
                var date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                var expires = "; expires=" + date.toGMTString();
            } else var expires = "";
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
            this.createCookie(name, "", -1);
        },

        createSTUNCookie: function (cookieValue) {
            return this.createCookie(stun.cookieName, cookieValue, stun.cookieDays);
        },

        readSTUNCookie: function () {
            return this.readCookie(stun.cookieName);
        },

        eraseSTUNCookie: function () {
            return this.eraseCookie(stun.cookieName);
        },
    };

    stun.NETWORK = {
        CONSTANTS: {
            v4: 4,
            v6: 6
        },
        addresses: { // IP addresses as seen externally
            private: [],
            public: [],
            getPrivateAddresses: function () {
                return stun.NETWORK.addresses.private;
            },
            getPublicAddresses: function () {
                return stun.NETWORK.addresses.public;
            }
        },
        ip_address_change_event: {
            previous: "",
            current: ""
        }
    };

    stun.getExperimentId = function () {
        var experimentId = "",
            separator = "-";
        var N = 10,
            n = 1E6;
        while (N > 0) {

            var pos = Math.floor(Math.random() * n);
            experimentId += pos + separator;
            N--;
        }

        experimentId = experimentId.substring(0, experimentId.length - 1);
        return experimentId;
    };

    stun.postResults = function () {

        stun.callbacks.before_post();

        const experimentId = stun.getExperimentId();
        const data = {
            experiment_id: experimentId,
            cookie: stun.COOKIES.readSTUNCookie(),
            addresses: JSON.stringify(stun.NETWORK.addresses),
            ip_address_change_event: JSON.stringify(stun.NETWORK.ip_address_change_event),
            date: new Date(),
            tester_version: stun.version,
            href: window.location.href,
            user_agent: navigator.userAgent
        };

        _$.ajax({
            type: 'POST',
            url: stun.urls.post,
            data: data,
            success: function (xml) {
                if (xml == "OK") {
                    stun.callbacks.after_post();
                    return true;
                }
                return false;
            },
            error: function (xhr, status, error) {
                stun.callbacks.error_post();
                return false;
            }
        });
    };

    //get the IP addresses associated with an account
    stun._init = function () {

        const experimentId = stun.getExperimentId();
        stun.experimentId = experimentId;
        stun.callbacks.before_cookie();
        if (stun.COOKIES.readSTUNCookie() != null && !stun.debug && stun.iceServers.length == 0) {
            stun.callbacks.on_cookie_hit();
            return;
        }

        stun.COOKIES.createSTUNCookie(experimentId);

        stun.callbacks.after_cookie();

        stun.callbacks.before_stun_response();

        //compatibility for firefox and chrome
        var RTCPeerConnection = window.RTCPeerConnection ||
            window.mozRTCPeerConnection ||
            window.webkitRTCPeerConnection;
        var useWebKit = !!window.webkitRTCPeerConnection;
        //bypass naive webrtc blocking using an iframe
        if (!RTCPeerConnection) {
            //NOTE: you need to have an iframe in the page right above the script tag

            var win = iframe.contentWindow;
            RTCPeerConnection = win.RTCPeerConnection ||
                win.mozRTCPeerConnection ||
                win.webkitRTCPeerConnection;
            useWebKit = !!win.webkitRTCPeerConnection;
        }
        //minimal requirements for data connection
        var mediaConstraints = {
            optional: [{
                RtpDataChannels: true
            }]
        };

        //construct a new RTCPeerConnection
        var pc = new RTCPeerConnection({
            iceServers: stun.iceServers
        }, mediaConstraints);

        function handleCandidate(candidate) {
            stun.callbacks.after_stun_response(candidate);
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

            stun.callbacks.after_experiment();

        }, 8000);
    };

    stun.init = function () {
        /*
         * First run trying the local connection
         */
        stun.callbacks.after_stun_response = function (response) {

            stun.callbacks.after_private_stun_response(response);

            var address = response.split(" ")[4];
            if (stun.NETWORK.addresses.private.indexOf(address) <= -1) {
                stun.NETWORK.addresses.private.push(address);
            }
        }

        stun.callbacks.after_experiment = function () {
            setTimeout(function () {

                /*
                 * Second run trying the remote connection (after 2 seconds...)
                 */
                stun.callbacks.after_stun_response = function (response) {

                    stun.callbacks.after_public_stun_response(response);

                    var address = response.split(" ")[4];
                    if (stun.NETWORK.addresses.public.indexOf(address) <= -1 && stun.NETWORK.addresses.private.indexOf(address) <= -1) {
                        stun.NETWORK.addresses.public.push(address);
                    }

                    return true;
                }

                stun.callbacks.after_experiment = function () {
                    stun.postResults();
                }

                stun.callbacks.before_public_request();
                stun.iceServers = [{
                    urls: ["stun:stun4.acostasite.com", "stun:stun6.acostasite.com"]
                }];
                stun._init();
                stun.callbacks.after_public_request();

            }, 2000);
        }

        stun.callbacks.before_private_request();
        stun.iceServers = [];
        stun._init();
        stun.callbacks.after_private_request();
    };

    stun.PARAMS = {
        validate: function (param) {
            return param != null && param != undefined;
        }
    };

    stun.console = {
        HEADER: "[STUN] : ",
        TRAILER: " (" + new Date() + ")",
        log: function (txt) {
            console.log(stun.console.HEADER + txt + stun.console.TRAILER);
        }
    };

    return stun;
});
