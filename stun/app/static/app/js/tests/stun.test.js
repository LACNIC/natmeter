/**
 * Created by agustin on 9/2/16.
 */

describe("Load suite", function () {

    requirejs.config({
        "paths": {
            "stun": "/static/app/js/stun"
        }
    });
    require(["stun"], function (_STUN) {
        STUN = _STUN;  // load STUN as a global variable
    });

    it("STUN has loaded correctly", function () {
        expect(STUN).toBeDefined();
    });

    it("jQuery has loaded correctly", function () {
        expect($).toBeDefined();
    });

    it("Public IP address", function () {

        iframe = document.createElement("iframe");
        iframe.setAttribute("id", "iframe");

        STUN.after_public_request = function () {
            expect(STUN.NETWORK.addresses.public).not.toEqual([]);
        }

        expect(STUN.NETWORK.addresses.public).toEqual([]);
        STUN.init();
    });

    it("Private IP address", function () {

        iframe = document.createElement("iframe");
        iframe.setAttribute("id", "iframe");

        STUN.after_stun_response = function () {
            expect(STUN.NETWORK.addresses.private).not.toEqual([]);
        }

        expect(STUN.NETWORK.addresses.private).toEqual([]);
        STUN.init();
    });

});

