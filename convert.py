########################################################
# Convert the modulo timestamp back to epoch time      #
# To be used with generate-test-traffic.py             #
########################################################

import time, datetime
current_epoch_time = int(time.time())
modulo = int(input("Enter the modulo timestamp: "))
epoch_timestamp = int((modulo / 65536.0 + int(current_epoch_time / 65536)) * 65536)
print(epoch_timestamp)
datetime_time = datetime.datetime.fromtimestamp(epoch_timestamp)
print(str(datetime_time)+" UTC")
