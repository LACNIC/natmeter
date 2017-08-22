# NAT Meter
NAT Meter is an attempt to measure 44 and 66 NAT (yes, 66 NAT) in the LAC region. It is based on JavaScript calls to STUN / TURN servers that provide information about the client's connection. Based on this [WebRTC project] (https://github.com/diafygi/webrtc-ips) by @diafygi.

## Collaborate
Embed the following script on your site, to let us trigger measurements form your visitors' browsers:
```javascript
<script src="https://cdn.dev.lacnic.net/lacnic-net-measurements.js"></script>
```

[![Code Health](https://landscape.io/github/LACNIC/natmeter/cookies/landscape.svg?style=flat)](https://landscape.io/github/LACNIC/natmeter/cookies)
[![Build Status](https://travis-ci.org/LACNIC/natmeter.svg?branch=cookies)](https://travis-ci.org/LACNIC/natmeter)
[![Coverage Status](https://coveralls.io/repos/github/LACNIC/natmeter/badge.svg?branch=master)](https://coveralls.io/github/LACNIC/natmeter?branch=master)
