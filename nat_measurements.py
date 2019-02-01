#!/usr/bin/python
import psycopg2
#note that we have to import the Psycopg2 extras library!
import psycopg2.extras
import sys
import ipaddress

#ip_address_kind. 1=host 2 = stun
host_addresses=[]
stun_addresses=[]


def AVGIPv6Host():
   #Find average number of IPv6 addresses in the clients
   SQLQUERY="Select AVG(y.AAAA) from (Select count(*) as AAAA from app_stunipaddress \
     WHERE family(ip_address)=6 and ip_address_kind=1 \
     GROUP BY stun_measurement_id) y "

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))

def AVGIPv4Host():
   #Find average number of IPv4 addresses in the clients
   SQLQUERY="Select AVG(y.AAAA) from (Select count(*) as AAAA from app_stunipaddress \
     WHERE family(ip_address)=4 and ip_address_kind=1 \
     GROUP BY stun_measurement_id) y "

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))



def MAXIPv6Host():
   #Find Max Number of IPv6 addresses in the host
   SQLQUERY="Select count(*), stun_measurement_id from app_stunipaddress \
     WHERE family(ip_address)=6 and ip_address_kind=1 \
     GROUP BY stun_measurement_id ORDER BY COUNT(*) DESC LIMIT 1"

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))

def MAXIPv4Host():
   #Find Max Number of IPv4 addresses in the host
   SQLQUERY="Select count(*), stun_measurement_id from app_stunipaddress \
     WHERE family(ip_address)=4 and ip_address_kind=1 \
     GROUP BY stun_measurement_id ORDER BY COUNT(*) DESC LIMIT 1"

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))


def FindDualStackHosts():
   #Find Dual Stack hosts
   SQLQUERY="Select * from app_stunipaddress t1 \
    WHERE (select count(*) from app_stunipaddress t2 where t1.stun_measurement_id=t2.stun_measurement_id \
    AND family(ip_address)=4)>0 and (select count(*) from app_stunipaddress t2 \
    WHERE t1.stun_measurement_id=t2.stun_measurement_id and family(ip_address)=6)>0  \
    AND (select count(*) from app_stunipaddress t3 where t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 )>0 "

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))


def FindIPv4OnlyHosts():
   #Find IPv4 Only Hosts
   SQLQUERY="Select * from app_stunipaddress t1 \
    WHERE (select count(*) from app_stunipaddress t2 where t1.stun_measurement_id=t2.stun_measurement_id \
    AND family(ip_address)=4)>0 and (select count(*) from app_stunipaddress t2 \
    WHERE t1.stun_measurement_id=t2.stun_measurement_id and family(ip_address)=6)=0  \
    AND (select count(*) from app_stunipaddress t3 where t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 )>0 "

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))

def FindIPv6OnlyHosts():
   #Find IPv4 Only Hosts
   SQLQUERY="Select * from app_stunipaddress t1 \
    WHERE (select count(*) from app_stunipaddress t2 where t1.stun_measurement_id=t2.stun_measurement_id \
    AND family(ip_address)=4)>0 and (select count(*) from app_stunipaddress t2 \
    WHERE t1.stun_measurement_id=t2.stun_measurement_id and family(ip_address)=4)=0  \
    AND (select count(*) from app_stunipaddress t3 where t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 )>0 "

   MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

   row_count=0
   for MEASUREMENT in MEASUREMENTS_IDs:  #We will interact for every MEASUREMENT
       row_count += 1
       print ("row  ", (row_count, MEASUREMENT))


def FindNAT66(NPT):
    #With the following query we look for host that sucessfully reach the STUN Server
    #Only find v6 addresses
    SQLQUERY="SELECT DISTINCT stun_measurement_id FROM app_stunipaddress \
      WHERE family(ip_address)=6 AND ip_address_kind = 2 AND ip_address is not null"

    SQLQUERY="Select DISTINCT stun_measurement_id from app_stunipaddress t1 \
     WHERE \
     (select count(*) from app_stunipaddress t2 \
     WHERE t1.stun_measurement_id=t2.stun_measurement_id and t2.ip_address_kind=2 and family(ip_address)=6)>0 \
     AND (select count(*) from app_stunipaddress t3 \
     WHERE t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 and family(ip_address)=6)>0 \
     AND family(ip_address)=6 AND ip_address is not null"

    MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

    for MEASUREMENT in MEASUREMENTS_IDs:  #Let's interact for every item in the record set
      #print ("Looking for NAT66 for MEASUREMENT:", MEASUREMENT[0])

      SQLQUERY="SELECT ip_address from app_stunipaddress \
       WHERE ip_address_kind = 2 AND family(ip_address)=6 AND stun_measurement_id =" + str(MEASUREMENT[0])
      stun_addresses=MAKEQUERYDB(SQLQUERY) # Retrieve a Record Set containing only the IPs from the STUN

      SQLQUERY="SELECT ip_address from app_stunipaddress \
       WHERE ip_address_kind = 1 AND family(ip_address)=6 AND stun_measurement_id =" + str(MEASUREMENT[0])
      host_addresses=MAKEQUERYDB(SQLQUERY) # Retrieve a Record Set containing only the IPs from the HOST

      #print ("LONGITUD", len(stun_addresses), len(host_addresses))
      if len(stun_addresses)==0 or len(host_addresses)==0: continue #Let's skip this interaction

      for item in stun_addresses:
         if item in host_addresses:  #In case the IP in the Stun is in the host not nat being happening
           pass
         else:
           if NPT==0:
             print ("Natted IPv6 Host ", item, "IPv6 private addresses: ",host_addresses)
             #Now let's see if NAT == NPT
           if NPT==1:
             for ip1 in host_addresses:
               #print ("EVALUANDO NPT EN NAT66 ", ip1[0], item[0])
               if is_npt(ip1[0],item[0]) != False:
                 print ("Host Nateado NAT66 y con NPT", ip1, item)

def is_npt(ip1, ip2):
  '''
  Buscar NPT (RFC 6296). 
  We compare the last 64 bits of each address. If they match there is NPT
  '''
  v6_1 = ipaddress.IPv6Address(ConvertToUnicode(ip1))
  v6_2 = ipaddress.IPv6Address(ConvertToUnicode(ip2))
  #print ("EVALUANDO NPT DENTRO DE LA FUNCION", ip1, ip2)
  #print (v6_1.exploded.split(":")[4:])
  #print (v6_1.exploded.split(":")[4:])
  #print ('v6_1: ', v6_1)
  #print ('v6_2: ', v6_2)
  return v6_1.exploded.split(":")[4:] == v6_2.exploded.split(":")[4:]
  #return

def ConvertToUnicode(item):
  #print (unicode(item))
  return(str(item))

def FindNAT44():
    #With the following query we look for host that sucessfully reach the STUN Server
    #Only find v4 addresses

    SQLQUERY="Select DISTINCT stun_measurement_id from app_stunipaddress t1 \
     WHERE \
     (select count(*) from app_stunipaddress t2 \
     WHERE t1.stun_measurement_id=t2.stun_measurement_id and t2.ip_address_kind=2 AND family(ip_address)=4)>0 \
     AND (select count(*) from app_stunipaddress t3 \
     WHERE t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 AND family(ip_address)=4)>0 \
     AND family(ip_address)=4  AND NOT (ip_address << '179.0.56.0/23' or ip_address << '200.0.86.0/23' or \
     ip_address << '200.0.88.0/24' or ip_address << '200.3.12.0/23' or ip_address << '200.7.86.0/23' or ip_address << '200.7.84.0/23' \
     or ip_address << '200.10.60.0/23' or ip_address << '200.10.62.0/23' ) "

    MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

    for MEASUREMENT in MEASUREMENTS_IDs:  #Let's interact for every item in the record set
      print ("Looking for NAT44 for MEASUREMENT:", MEASUREMENT[0])

      SQLQUERY="SELECT ip_address from app_stunipaddress \
       WHERE ip_address_kind = 2 AND family(ip_address)=4 AND stun_measurement_id =" + str(MEASUREMENT[0])
      stun_addresses=MAKEQUERYDB(SQLQUERY) # Retrieve a Record Set containing only the IPs from the STUN

      SQLQUERY="SELECT ip_address from app_stunipaddress \
       WHERE ip_address_kind = 1 AND family(ip_address)=4 AND stun_measurement_id =" + str(MEASUREMENT[0])
      host_addresses=MAKEQUERYDB(SQLQUERY) # Retrieve a Record Set containing only the IPs from the HOST

      #print ("LONGITUD", len(stun_addresses), len(host_addresses))
      if len(stun_addresses)==0 or len(host_addresses)==0: continue #Let's skip this interaction

      for item in stun_addresses:
         if item in host_addresses:  #In case the IP in the Stun is in the host not nat being happening
           pass
         else:
           print ("Natted IPv4 Host", host_addresses, "public", stun_addresses)
 
def main():

    RunMeasurement()


def NONAT44():
    '''
    The object of this functin is to find hosts with no NAT44
    '''
    #With the following query we look for hosts that has nothing as ip_address_kind=2
    #but have IPs as ip_address_kind=1
    SQLQUERY="Select * from app_stunipaddress t1 \
     WHERE \
     (select count(*) from app_stunipaddress t2 \
     WHERE t1.stun_measurement_id=t2.stun_measurement_id and t2.ip_address_kind=2 AND family(ip_address)=4 )=0  \
     AND (select count(*) from app_stunipaddress t3 \
     WHERE t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 AND family(ip_address)=4)>0 \
     AND family(ip_address)=4 AND NOT (ip_address << '179.0.56.0/23' or ip_address << '200.0.86.0/23' or \
     ip_address << '200.0.88.0/24' or ip_address << '200.3.12.0/23' or ip_address << '200.7.86.0/23' or ip_address << '200.7.84.0/23' \
     or ip_address << '200.10.60.0/23' or ip_address << '200.10.62.0/23' ) "

    MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

    for MEASUREMENT in MEASUREMENTS_IDs:  #Let's interact for every item in the record set
      ip1=ipaddress.ip_address(ConvertToUnicode(MEASUREMENT[1]))
      if not ip1.is_private:
        print ("NONAT44 for MEASUREMENT:", ip1)

def NONAT66():
    '''
    The object of this functin is to find hosts with no NAT44
    '''
    #With the following query we look for hosts that has nothing as ip_address_kind=2
    #but have IPs as ip_address_kind=1
    SQLQUERY="Select * from app_stunipaddress t1 \
     WHERE \
     (select count(*) from app_stunipaddress t2 \
     WHERE t1.stun_measurement_id=t2.stun_measurement_id and t2.ip_address_kind=2 AND family(ip_address)=6)=0 \
     AND (select count(*) from app_stunipaddress t3 \
     WHERE t1.stun_measurement_id=t3.stun_measurement_id and t3.ip_address_kind=1 AND family(ip_address)=6 )>0 \
     AND family(ip_address)=6"

    MEASUREMENTS_IDs = MAKEQUERYDB(SQLQUERY)

    for MEASUREMENT in MEASUREMENTS_IDs:  #Let's interact for every item in the record set
      ip1=ipaddress.ip_address(ConvertToUnicode(MEASUREMENT[1]))
      if not ip1.is_private:
        print ("Looking for NONAT66 for MEASUREMENT:", ip1)



def RunMeasurement():
  NPT=0
  if sys.argv[1] == "NAT44":
     FindNAT44()
  if sys.argv[1] == "NAT66":
     FindNAT66(NPT)
  if sys.argv[1] == "NPT":
     NPT=1
     FindNAT66(NPT)
  if sys.argv[1] == "NONAT44":
     NONAT44()
  if sys.argv[1] == "NONAT66":
     NONAT66()
  if sys.argv[1] == "DualStackHosts":
     FindDualStackHosts()
  if sys.argv[1] == "IPv4OnlyHosts":
     FindIPv4OnlyHosts()
  if sys.argv[1] == "IPv6OnlyHosts":
     FindIPv6OnlyHosts()
  if sys.argv[1] == "MAXIPv6Host":
     MAXIPv6Host()
  if sys.argv[1] == "MAXIPv4Host":
     MAXIPv4Host()
  if sys.argv[1] == "AVGIPv6Host":
     AVGIPv6Host()
  if sys.argv[1] == "AVGIPv4Host":
     AVGIPv4Host()


  exit()  #In case the parameter received is none of the above


def MAKEQUERYDB(SQLQUERY):
  '''
  Simple function that receives an SQLQUERY and return a recordset
  '''
  conn_string = "host='localhost' dbname='stun' user='alejandro' password='alejandro'"
  #print "Connecting to database\n	->%s" % (conn_string)
  conn = psycopg2.connect(conn_string)
  conn = psycopg2.connect(conn_string)
  cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
  cursor.execute(SQLQUERY)
  rows = cursor.fetchall()
  cursor.close()
  return rows


if __name__ == "__main__":
  if len(sys.argv) == 2:
    main()
  else:
    print ("Wrong number of parameters")
