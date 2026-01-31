from weartsdk import WeArtCommon
from weartsdk.WeArtClient import WeArtClient
from weartsdk.WeArtTrackingCalibration import WeArtTrackingCalibration
from weartsdk.WeArtThimbleTrackingObject import WeArtThimbleTrackingObject
from weartsdk.TDProStatusListener import TDProStatusListener
from weartsdk.MiddlewareStatusListener import MiddlewareStatusListener
import logging
import time


client = WeArtClient(WeArtCommon.DEFAULT_IP_ADDRESS, WeArtCommon.DEFAULT_TCP_PORT, log_level=logging.INFO)
client.Run()

mwListener = MiddlewareStatusListener()
client.AddMessageListener(mwListener)

tdpListener = TDProStatusListener()
client.AddMessageListener(tdpListener)

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

input("Put on device, enter when done")
calibration = WeArtTrackingCalibration()
client.AddMessageListener(calibration)
client.StartCalibration()
while(not calibration.getResult()):
    time.sleep(1)
print(f"Calibrated: {calibration.getResult()}")
client.StopCalibration()

# Closure Tracking for all 5 fingers, (LEFT HAND)
thumbThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Thumb)
client.AddThimbleTracking(thumbThimbleTracking)
indexThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Index)
client.AddThimbleTracking(indexThimbleTracking)
middleThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Middle)
client.AddThimbleTracking(middleThimbleTracking)
annularThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Annular)
client.AddThimbleTracking(annularThimbleTracking)
pinkyThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Left, WeArtCommon.ActuationPoint.Pinky)
client.AddThimbleTracking(pinkyThimbleTracking)

# Print abduction and closure values for 60 seconds
for _ in range(120):
    print("THUMB CLOSURE: " + str(thumbThimbleTracking.GetClosure()) + ";  THUMB ABDUCTION: " + str(thumbThimbleTracking.GetAbduction()))
    print("INDEX CLOSURE: " + str(indexThimbleTracking.GetClosure()))
    print("MIDDLE CLOSURE: " + str(middleThimbleTracking.GetClosure()))
    print("ANNULAR CLOSURE: " + str(annularThimbleTracking.GetClosure()))
    print("PINKY CLOSURE: " + str(pinkyThimbleTracking.GetClosure()))
    time.sleep(0.5)

client.Stop()
client.Close()















