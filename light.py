import RPi.GPIO as GPIO
import time

class Light(object):


    def __init__(self, pin=23):
        self.RelayPin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RelayPin,GPIO.OUT, initial=GPIO.LOW)


    def turn_off(self):
        print ('|******************|')
        print ('|  ...Relay close  |')
        print ('|******************|\n')

        GPIO.output(self.RelayPin,GPIO.LOW)
        time.sleep(1)

    def turn_on(self):
        print ('|*****************|')
        print ('|  Relay open...  |')
        print ('|*****************|\n')
        print ('')
        GPIO.output(self.RelayPin,GPIO.HIGH)
        time.sleep(5)

            #define a destroy function for clean up everything after the script finished
    def destroy():
        #turn off relay
        GPIO.output(self.RelayPin,GPIO.LOW)
        #release resource
        GPIO.cleanup()
    #
    # if run this script directly ,do:
    # if __name__ == '__main__':
    #     setup()
    #     try:
    #             main()
    #     #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    #     except KeyboardInterrupt:
    #         destroy()
