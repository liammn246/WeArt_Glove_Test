from weartsdk import WeArtCommon
from weartsdk.WeArtClient import WeArtClient
from weartsdk.WeArtTrackingCalibration import WeArtTrackingCalibration
from weartsdk.WeArtThimbleTrackingObject import WeArtThimbleTrackingObject
from weartsdk.TDProStatusListener import TDProStatusListener
from weartsdk.MiddlewareStatusListener import MiddlewareStatusListener
import logging
import time
import socket
import struct


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

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq = 0


def closure_to_byte(val):
    """
    Map closure in [0.0, 1.0] to 0-255 (uint8). Clamp out-of-range or invalid values to 0..255.
    """
    # handles if the float is NaN, sets to safe value 0.0
    if val != val:
        val = 0.0
    # Scales value to unsigned bit range of 0-255
    b = int(round(val * 255.0))
    return max(0, min(255, b))

for _ in range(120):
    thumb_f = thumbThimbleTracking.GetClosure()
    index_f = indexThimbleTracking.GetClosure()
    middle_f = middleThimbleTracking.GetClosure()
    ring_f = annularThimbleTracking.GetClosure()
    pinky_f = pinkyThimbleTracking.GetClosure()
    t = closure_to_byte(thumb_f)
    i = closure_to_byte(index_f)
    m = closure_to_byte(middle_f)
    r = closure_to_byte(ring_f)
    p = closure_to_byte(pinky_f)

    # Send closure values as [seq:uint8][thumb:uint8][index:uint8][middle:uint8][ring:uint8][pinky:uint8]
    pkt = struct.pack('!6B', seq, t, i, m, r, p)
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    seq = (seq + 1) % 256
    time.sleep(0.5)

sock.close()

client.Stop()
client.Close()