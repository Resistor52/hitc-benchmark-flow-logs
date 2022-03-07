#############################################################################################
# Generate TCP traffic such that the source port is a timestamp that can be used to         #
# benchmark a remote flow logging system. One packet per second.  Must be run as root!      #
# www.kennethghartman.com    |    www.headintheclouds.site   |   @kennethghartman           #
#############################################################################################

import time, sys, signal, pytz
from datetime import datetime
from scapy.all import send,IP,TCP

# Global Variables
tz_TZ = pytz.timezone('UTC') # Change 'UTC' to your timezone; Use UTC for AWS
errMsg0='ERROR\nTime entries must be in the format of "HH:MM" \nExiting'
errMsg1='ERROR\nTime entries must be in the format of "HH:MM" \nInvalid "HH"\nExiting'
errMsg2='ERROR\nTime entries must be in the format of "HH:MM" \nInvalid "MM"\nExiting'
errMsg3='ERROR\nTime entries must be in the future (greater than the current time of day)\nExiting'
errMsg4='ERROR\nEnd Time entry must after the Start Time entry\nExiting'
errMsg5='ERROR\nTarget IP address must be in the format of "111.111.111.111" \nExiting'
errMsg6='ERROR\nTarget IP address contains an invalid octet\nExiting'
errMsg7='ERROR\nThe Length of the Name of the Logfile cannot be zero\nExiting'
errMsg8='ERROR\nEnter the log file name without the ".csv" extension\nExiting'

# Functions
def handler(signum, frame):
    "Handle a control-c to escape the infinite loop"
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        f.close() # gracefully close the open log file before exiting
        print(f"Packet timestamps are logged as {logfile}.csv")
        exit(1)

def validateLogFileName(log_file):
    "Validate the name of the log file entered"
    if len(log_file) == 0:
        sys.exit(errMsg7)
    entry = log_file.split(".")
    if entry[-1] == "csv":
        sys.exit(errMsg8)

def validateIPtarget(ip_address):
    "Validate the IP address entered"
    if "." not in ip_address:
        sys.exit(errMsg5)
    entry = ip_address.split(".")
    if len(entry) != 4:
        sys.exit(errMsg5)
    for octet in entry:
        try:
            int(octet)
        except:
            sys.exit(errMsg6)
        if int(octet) > 255:
            sys.exit(errMsg6)
        if int(octet) < 0:
            sys.exit(errMsg6)
    return

def validateTimeEntry(timeEntry):
    "Validate the time entered and return the corresponding epoch time"
    if ":" not in timeEntry:
        sys.exit(errMsg0)
    entry=timeEntry.split(":")
    if len(entry) != 2:
        sys.exit(errMsg0)
    try:
        int(entry[0])
    except:
        sys.exit(errMsg1)
    try:
        int(entry[1])
    except:
        sys.exit(errMsg2)
    if int(entry[0]) > 23:
        sys.exit(errMsg1)
    if int(entry[0]) < 0:
        sys.exit(errMsg1)
    if int(entry[1]) > 59:
        sys.exit(errMsg2)
    if int(entry[1]) < 0:
        sys.exit(errMsg2)

    #Determine Seconds since midnight
    seconds=int(entry[0])*60*60 + int(entry[1])*60

    #Determine Epoch Time at last Midnight
    epochTime_now = time.time()
    local_time_now = time.localtime(epochTime_now)
    midnight = (local_time_now.tm_year, local_time_now.tm_mon, local_time_now.tm_mday, 0, 0, 0, local_time_now.tm_wday, local_time_now.tm_yday, local_time_now.tm_isdst)
    local_time_midnight = time.mktime(midnight)
    epochTime = seconds + local_time_midnight
    if epochTime_now >= epochTime:
        sys.exit(errMsg3)
    return epochTime

def RemainingTimeString(time_epoch):
    "Determine the remaining time string"
    epochTime_now = time.time()
    remainingSeconds = time_epoch - epochTime_now
    if remainingSeconds < 60:
        remainingSeconds = int(remainingSeconds)
        timeString=f"Remaining Time: {remainingSeconds} Seconds      "
    else:
        remainingMinutes = int(remainingSeconds / 60)
        remainingSeconds = int(remainingSeconds % 60)
        if remainingMinutes <60:
            timeString=f"Remaining Time: {remainingMinutes}:{remainingSeconds}    "
        else:
            remainingHours = int(remainingMinutes / 60)
            remainingMinutes = int(remainingMinutes % 60)
            timeString=f"Remaining Time: {remainingHours}:{remainingMinutes}:{remainingSeconds}"
    return timeString

def startCountdown(start_time_epoch):
    "Count down to start of traffic generation"
    print(f"Traffic generation will start at: {startTime}")
    epochTime_now = time.time()
    while epochTime_now < start_time_epoch:
        epochTime_now = time.time()
        print(RemainingTimeString(start_time_epoch), end = "\r")
    return

def stopCountdown(stop_time_epoch):
    epochTime_now = time.time()
    while epochTime_now < stop_time_epoch:
        epochTime_now = time.time()
        generateTraffic(stop_time_epoch)
    return

def generateTraffic(stop_time_epoch):
    datetime_TZ = datetime.now(tz_TZ)
    seconds = int(time.time())             # Current Epoch Time
    modulo = seconds % (2 ** 16)           # Calculate the SrcPort
    datetime_time=datetime_TZ.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    print(f"Epoch Time: {seconds}   Time: {datetime_time}   srcPort: {modulo}   {RemainingTimeString(stop_time_epoch)}      ", end = "\r")
    write_str='"'+str(seconds)+'","'+datetime_time+'","'+str(modulo)+'"\n'
    f.write(write_str)
    tcp=TCP(sport=modulo,dport=7777,flags="S",options=[('Timestamp',(0,0))])
    pay=logfile+" - "+str(modulo)
    # Trap the output of scapy send so it does not print to console
    state = sys.stdout
    sys.stdout = open('/dev/null', 'w')
    send(ip/tcp/pay)                       # Scapy
    sys.stdout.close()
    sys.stdout = state
    # Wait one second between packets
    time.sleep(1)
    return

# Main program
signal.signal(signal.SIGINT, handler)
logfile = input('Enter the name for the CSV log file (without the csv extension): ')
validateLogFileName(logfile)
ip_address = input('Enter the desired target IP aggress in the format "111.111.111.111": ')
validateIPtarget(ip_address)
startTime = input('Enter the desired start time in the format "HH:MM" for local time zone: ')
startTimeEpoch = validateTimeEntry(startTime)
endTime = input('Enter the desired end time in the format "HH:MM" for local time zone: ')
endTimeEpoch = validateTimeEntry(endTime)
if endTimeEpoch < startTimeEpoch:
    sys.exit(errMsg4)
startCountdown(startTimeEpoch)
print(f"Traffic generation will continue until: {endTime}")
print("**************** Start of Traffic **************************")
f = open(logfile+".csv", "w")
f.write('"Epoch_Time","Date_Time","Source_Port"\n')
ip=IP(dst=ip_address)
# generate Traffic and start the Stop Countdown
stopCountdown(endTimeEpoch)
print("\n***************** End of Traffic ***************************")
