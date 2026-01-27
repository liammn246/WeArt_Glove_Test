from weartsdk import WeArtCommon
from weartsdk.WeArtClient import WeArtClient
from weartsdk.WeArtTrackingCalibration import WeArtTrackingCalibration
from weartsdk.WeArtThimbleTrackingObject import WeArtThimbleTrackingObject
from weartsdk.WeArtTrackingRawData import WeArtTrackingRawData
from weartsdk.TDProStatusListener import TDProStatusListener
from weartsdk.MiddlewareStatusListener import MiddlewareStatusListener
import logging
import time


client = WeArtClient(WeArtCommon.DEFAULT_IP_ADDRESS, WeArtCommon.DEFAULT_TCP_PORT, log_level=logging.INFO)
client.Run()


# Set up WeArt App Listener, and the Glove Device Listener
mwListener = MiddlewareStatusListener()
client.AddMessageListener(mwListener)


tdpListener = TDProStatusListener()
client.AddMessageListener(tdpListener)


# Checks for Connection before running code. Print some device info before begin
middlewareStatus = mwListener.LastStatus()
if len(middlewareStatus.connectedDevices) == 0:
    print("Waiting for device to be connected...")
    while len(middlewareStatus.connectedDevices) == 0:
        time.sleep(0.5)
        middlewareStatus = mwListener.LastStatus()
deviceStatus = tdpListener.LastStatus()
for i, device in enumerate(deviceStatus.devices):
    print(f"Device {i} connected with MAC address {device.macAddress}, hand side {device.handSide} has battery at {device.master.batteryLevel}%")


client.Start()


# User must now put on device
input("Put on device, enter when done")


# Begin calibration phase
calibration = WeArtTrackingCalibration()
client.AddMessageListener(calibration)
client.StartCalibration()
while(not calibration.getResult()):
    time.sleep(1)
print(f"Calibrated: {calibration.getResult()}")
client.StopCalibration()

# Istantiate a ThimbeTrackingObject to read closure and abductions value from the thumb, and index
thumbThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Thumb)
client.AddThimbleTracking(thumbThimbleTracking)
indexThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Index)
client.AddThimbleTracking(indexThimbleTracking)

# Print abduction and closure values for 10 seconds
for _ in range(20):
    print("THUMB ABDUCTION: " + str(thumbThimbleTracking.GetAbduction()))
    print("THUMB CLOSURE: " + str(thumbThimbleTracking.GetClosure()))
    # Only thumb has abduction values, so for index print only closure
    print("INDEX CLOSURE: " + str(indexThimbleTracking.GetClosure()))
    time.sleep(0.5)

# Instantiate tracking raw data to read tracking raw data from the thimble's sensors
thumbRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Thumb)
client.AddMessageListener(thumbRawSensorData)

client.StartRawData()
ts = thumbRawSensorData.GetLastSample().timestamp
while ts == 0:
    time.sleep(1)
    ts = thumbRawSensorData.GetLastSample().timestamp
for _ in range (20):
    thumbSampleData = thumbRawSensorData.GetLastSample().data
    thumb_acc = thumbSampleData.accelerometer
    thumb_gyro = thumbSampleData.gyroscope
    print(f"THUMB:\n\tAcc:\n\t\tX: {thumbSampleData.accelerometer.x}\n\t\tY: {thumbSampleData.accelerometer.y}\n\t\tZ: {thumbSampleData.accelerometer.z}\n\tGyro:\n\t\tX: {thumbSampleData.gyroscope.x}\n\t\tY: {thumbSampleData.gyroscope.y}\n\t\tZ: {thumbSampleData.gyroscope.z}")
    time.sleep(0.5)

client.StopRawData()

client.Stop()
client.Close() #Close connection to middleware















