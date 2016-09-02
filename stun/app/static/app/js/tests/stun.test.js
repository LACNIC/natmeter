/**
 * Created by agustin on 9/2/16.
 */

describe("Load suite", function () {

    it("STUN has loaded correctly", function () {
        expect(STUN).toBeDefined();
    });

    it("STUN has loaded correctly", function () {
        expect($).toBeDefined();
    });

    it("Public IP address", function () {

        iframe = document.createElement("iframe");
        iframe.setAttribute("id", "iframe");

        STUN.after_public_ip = function () {
            expect(STUN.NETWORK.addresses).not.toEqual([]);
        }
        expect(STUN.NETWORK.addresses).toEqual([]);

        STUN.init();
    });
    it("STUN response frome STUN servers", function () {

        iframe = document.createElement("iframe");
        iframe.setAttribute("id", "iframe");

        STUN.after_stun_response = function () {
            expect(STUN.results).not.toEqual([]);
        }

        expect(STUN.results).toEqual([]);
        STUN.init();
    });

});

