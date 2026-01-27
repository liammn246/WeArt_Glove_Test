
from weartsdk import WeArtCommon
from weartsdk.WeArtClient import WeArtClient
from weartsdk.WeArtTrackingCalibration import WeArtTrackingCalibration
from weartsdk.WeArtThimbleTrackingObject import WeArtThimbleTrackingObject
from weartsdk.WeArtTrackingRawData import WeArtTrackingRawData
from weartsdk.TDProStatusListener import TDProStatusListener
from weartsdk.MiddlewareStatusListener import MiddlewareStatusListener
import logging
import time
import sys, os
import threading

sys.path.append(os.path.abspath(".."))

# Create appropriate events
deviceConnected = threading.Event()
calibrationFinished = threading.Event()

# Create appropriate callbacks
def mwStatusUpdateCallback(status):
    print("Middleware status updated at: " + str(status.timestamp))
    print("Middleware status is: " + str(status.status))
    if len(status.connectedDevices) > 0:
        print("There are " + str(len(status.connectedDevices)) + " connected devices")
        deviceConnected.set()

def tdProStatusUpdateCallback(status):
	print("Device status updated at: " + str(status.timestamp))
	print("There are " + str(len(status.devices)) + " connected devices")
	if len(status.devices) > 0:
		for device in status.devices:
			print("Device MAC address is: " + str(device.macAddress))
			print("Device hand side is: " + str(device.handSide))
			print("Device signal strength is: " + str(device.signalStrength))
			print("Device battery level is: " + str(device.master.batteryLevel))

def calibrationStatusCallback(handside, status):
        print(f"Calibration status for {str(handside)} hand is {str(status)}")

def calibrationResultCallback(handside, result):
	# result == True means that the calibration has successfully finished
	if(result):
		print(f"Calibration successfully completed for {str(handside)} hand!")
		# Set the event to signal the calibration is finished
		calibrationFinished.set()

if __name__ == '__main__':
    
    # Istantiate TCP/IP client to communicate with the Middleware
    client = WeArtClient(WeArtCommon.DEFAULT_IP_ADDRESS, WeArtCommon.DEFAULT_TCP_PORT, log_level=logging.INFO)
    client.Run()

    # Listener to receive data status from Middleware
    mwListener = MiddlewareStatusListener()
    # Callback to print the status when changes
    mwListener.AddStatusCallback(mwStatusUpdateCallback)
    client.AddMessageListener(mwListener)

    # Listener to receive data status from Device(s)
    tdpListener = TDProStatusListener()
    # Calllback to print the status when changes
    tdpListener.AddStatusCallback(tdProStatusUpdateCallback)
    client.AddMessageListener(tdpListener)

    # Wait for device(s) to be connected for at most 30 seconds
    if not deviceConnected.wait(30):
         print("No device connected!")
         exit(-1)

    # Wait for status messages to be received
    time.sleep(3)
    
    # Start the device(s)
    client.Start()

    # Wait for status messages to be received before print this input
    time.sleep(1)
    # Ask the user to wear the device(s) before starting the calibration
    input("Wear the device(s) and press Enter to start calibration...")

    # Calibration manager 
    calibration = WeArtTrackingCalibration()
    calibration.AddStatusCallback(calibrationStatusCallback)
    calibration.AddResultCallback(calibrationResultCallback)
    client.AddMessageListener(calibration)
    # Start Calibration Finger tracking algorithm
    client.StartCalibration()

    # Wait for calibration result with a timeout of 10 seconds
    if not calibrationFinished.wait(10):
        print("Calibration timeout expired!")
        exit(-1)
    
    # Stop calibration
    client.StopCalibration()

    # Istantiate a ThimbeTrackingObject to read closure and abductions value from the thumb
    thumbThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Thumb)
    # Add the thimble tracking object to the client
    client.AddThimbleTracking(thumbThimbleTracking)
    # Istantiate a ThimbeTrackingObject to read closure value from the index
    indexThimbleTracking = WeArtThimbleTrackingObject(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Index)
    # Add the thimble tracking object to the client
    client.AddThimbleTracking(indexThimbleTracking)

    # Print abduction and closure values for 10 seconds
    for _ in range(20):
        print("THUMB ABDUCTION: " + str(thumbThimbleTracking.GetAbduction()))
        print("THUMB CLOSURE: " + str(thumbThimbleTracking.GetClosure()))
        # Only thumb has abduction values, so for index print only closure
        print("IDEX CLOSURE: " + str(indexThimbleTracking.GetClosure()))
        time.sleep(0.5)

    # Instantiate tracking raw data to read tracking raw data from the thimble's sensors
    thumbRawSensorData = WeArtTrackingRawData(WeArtCommon.HandSide.Right, WeArtCommon.ActuationPoint.Thumb)
    client.AddMessageListener(thumbRawSensorData)

    # Activates raw data transmission
    client.StartRawData()

    # Wait until the first sample is received
    ts = thumbRawSensorData.GetLastSample().timestamp
    while ts == 0:
        time.sleep(1)
        ts = thumbRawSensorData.GetLastSample().timestamp
    
    # Print raw data for 10 seconds
    for _ in range (20):
        thumbSampleData = thumbRawSensorData.GetLastSample().data
        
        thumb_acc = thumbSampleData.accelerometer
        thumb_gyro = thumbSampleData.gyroscope

        print(f"THUMB:\n\tAcc:\n\t\tX: {thumbSampleData.accelerometer.x}\n\t\tY: {thumbSampleData.accelerometer.y}\n\t\tZ: {thumbSampleData.accelerometer.z}\n\tGyro:\n\t\tX: {thumbSampleData.gyroscope.x}\n\t\tY: {thumbSampleData.gyroscope.y}\n\t\tZ: {thumbSampleData.gyroscope.z}")

        time.sleep(0.5)

    client.StopRawData()
    time.sleep(1)

    client.Stop()
    client.Close()