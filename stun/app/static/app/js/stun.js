/**
 * Created by agustin on 5/31/16.
 */

STUN = {};
STUN.debug = true;
STUN = {

    urls: {
        post: STUN.debug && "http://127.0.0.1:8000/post/" || "https://natmeter.labs.lacnic.net/post/",
        ipv6ResolveURL: "http://simon.v6.labs.lacnic.net/cemd/getip/jsonp/",
        ipv4ResolveURL: "https://simon.v4.labs.lacnic.net/cemd/getip/jsonp/"
    },

    callbacks: {
        before_stun_response: function () {

        },
        after_stun_response: function (line) {

        },
        before_public_ip: function () {

        },
        after_public_ip: function (ip) {

        },
        before_post: function () {
            
        },
        after_post: function () {
            
        }
    },

    results: [],

    COOKIES: {

        cookieName: "lacnic-stun-cookie",
        cookieDays: 14,

        manageCookie: function () {
            /*
             * gets or sets the cookie
             */
            STUN.NETWORK.getMyIPAddress(null, function(ip) {
                /*
                 * (after) async call with callback...
                 */

                const currentIPAddress = ip;
                const previousIPAddress = STUN.COOKIES.readCookie(STUN.COOKIES.cookieName);

                if (previousIPAddress != null && STUN.NETWORK.prefixesMatch(previousIPAddress, currentIPAddress)) {

                    // do nothing

                } else {
                    // create or re-create the cookie
                    STUN.COOKIES.createCookie(STUN.COOKIES.cookieName, currentIPAddress, STUN.COOKIES.cookieDays);
                }
            });
        },
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

    NETWORK: {
        CONSTANTS: {
            v4: 4,
            v6: 6
        },
        addresses: [], // IP addresses as seen externally
        prefixesMatch: function (address1, address2) {

            if (!(STUN.PARAMS.validate(address1) && STUN.PARAMS.validate(address2))) {
                return false;
            }

            if (STUN.NETWORK.addressVersion(address1) != STUN.NETWORK.addressVersion(address2)) {
                return false;
            }

            // same address version...
            if (STUN.NETWORK.addressVersion(address1) == STUN.NETWORK.CONSTANTS.v4) {

                const octets = [1, 2, 3];
                const octets1 = address1.split(".");
                const octets2 = address2.split(".");

                // TODO check...
                octets.forEach(
                    function (o) {
                        if (octets1[o] != octets2[o]) {
                            return false;
                        }
                    }
                );

                return true;
            }

            if (STUN.NETWORK.addressVersion(address1) == STUN.NETWORK.CONSTANTS.v6) {
                // TODO implement this part...
                return true;
            }

        },
        addressVersion: function (address) {

            var _error = 0;

            if (!address) {
                return _error;
            }

            if (address.indexOf(":") > -1) {
                return STUN.NETWORK.CONSTANTS.v6;
            } else if (address.indexOf(".") > -1) {
                return STUN.NETWORK.CONSTANTS.v4;
            } else {
                return _error;
            }
        },

        getMyIPAddress: function (url, callback) {

            STUN.callbacks.before_public_ip();

            if (!url) {
                // default value
                url = STUN.urls.ipv6ResolveURL;
            }
            STUN.console.log(url);

            $.ajax({
                type: 'GET',
                url: url,
                dataType: 'jsonp',
                timeout: 5000,
                crossDomain: true,
                context: this,
                success: function (data) {

                    if (!data.ip || data.ip === null || data.ip == undefined) {
                        // error
                        this.error(null, "Error getting one of the IP addresses", "Error: IP address not gotten");
                    }


                    STUN.NETWORK.addresses.push(data.ip);

                    if (callback) {
                        STUN.callbacks.after_public_ip(data.ip);
                        callback(data.ip);
                    }
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    if (url != STUN.urls.ipv4ResolveURL) {
                        STUN.NETWORK.getMyIPAddress(STUN.urls.ipv4ResolveURL, callback);
                    }
                },
                complete: function () {

                }
            });
        },
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

        const payload = "[\"" + STUN.results.join("\",\"") + "\"]";
        const experimentId = STUN.getExperimentId();
        const cookie = STUN.COOKIES.readCookie(STUN.COOKIES.cookieName);
        const data = {
            data: payload,
            experiment_id: experimentId,
            cookie: cookie,
            tester_version: 1
        };

        $.ajax({
            type: 'POST',
            url: STUN.urls.post,
            data: data,
            success: function (xml) {
                STUN.callbacks.after_post();
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
        STUN.COOKIES.manageCookie();


        STUN.callbacks.before_stun_response();
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
        var servers = {iceServers: [{urls: ["stun:stun4.acostasite.com", "stun:stun6.acostasite.com"]}]};
        //construct a new RTCPeerConnection
        var pc = new RTCPeerConnection(servers, mediaConstraints);

        function handleCandidate(candidate) {
            callback(candidate);
            STUN.callbacks.after_stun_response(candidate);
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

        }, 8000);
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