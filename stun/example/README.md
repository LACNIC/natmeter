Natmeter measurements should be able to work using any STUN Server in Internet, however if you wish to use you own Stun Server we suggest STUNTMAN (http://www.stunprotocol.org/).

Also be aware that for this project you will need two STUN Servers, one in IPv6 and one in IPv4. STUNTMANT supports both.

After you successfully installed STUNTMANT the way we run it is:

IPv4:
cd /PATHTOSTUNTMAN; nohup ./stunserver --family 4 &

IPv6:
cd /PATHTOSTUNTMAN; nohup ./stunserver --family 6 &
