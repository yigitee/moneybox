import jetson.inference
import jetson.utils
import time
import atexit
from Adafruit_MotorHAT import Adafruit_MotorHAT #there is rm, so need to reload everytime
import traitlets
from traitlets.config.configurable import Configurable
from traitlets.config.configurable import SingletonConfigurable

# motor movement, look at Jetbot tutorial. Link in readme
class Motor(Configurable):

    value = traitlets.Float()
    
    # config
    alpha = traitlets.Float(default_value=1.0).tag(config=True)
    beta = traitlets.Float(default_value=0.0).tag(config=True)

    def __init__(self, driver, channel, *args, **kwargs):
        super(Motor, self).__init__(*args, **kwargs)  # initializes traitlets

        self._driver = driver
        self._motor = self._driver.getMotor(channel)
        if(channel == 1):
            self._ina = 1
            self._inb = 0
        else:
            self._ina = 2
            self._inb = 3
        atexit.register(self._release)
        
    @traitlets.observe('value')
    def _observe_value(self, change):
        self._write_value(change['new'])

    def _write_value(self, value):
        """Sets motor value between [-1, 1]"""
        mapped_value = int(255.0 * (self.alpha * value + self.beta))
        speed = min(max(abs(mapped_value), 0), 255)
        self._motor.setSpeed(speed)
        if mapped_value < 0:
            self._motor.run(Adafruit_MotorHAT.FORWARD)
            # The two lines below are required for the Waveshare JetBot Board only
            self._driver._pwm.setPWM(self._ina,0,0)
            self._driver._pwm.setPWM(self._inb,0,speed*16)
        else:
            self._motor.run(Adafruit_MotorHAT.BACKWARD)
            # The two lines below are required for the Waveshare JetBot Board only
            self._driver._pwm.setPWM(self._ina,0,speed*16)
            self._driver._pwm.setPWM(self._inb,0,0)

    def _release(self):
        """Stops motor by releasing control"""
        self._motor.run(Adafruit_MotorHAT.RELEASE)
        # The two lines below are required for the Waveshare JetBot Board only
        self._driver._pwm.setPWM(self._ina,0,0)
        self._driver._pwm.setPWM(self._inb,0,0)


class Robot(SingletonConfigurable):
    
    left_motor = traitlets.Instance(Motor)
    right_motor = traitlets.Instance(Motor)

    # config
    i2c_bus = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_channel = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)
    right_motor_channel = traitlets.Integer(default_value=2).tag(config=True)
    right_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)
    
    def __init__(self, *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self.motor_driver = Adafruit_MotorHAT(i2c_bus=self.i2c_bus)
        self.left_motor = Motor(self.motor_driver, channel=self.left_motor_channel, alpha=self.left_motor_alpha)
        self.right_motor = Motor(self.motor_driver, channel=self.right_motor_channel, alpha=self.right_motor_alpha)
        
    def set_motors(self, left_speed, right_speed):
        self.left_motor.value = left_speed
        self.right_motor.value = right_speed
        
    def forward(self, speed=1.0, duration=None):
        self.left_motor.value = speed
        self.right_motor.value = speed

    def backward(self, speed=1.0):
        self.left_motor.value = -speed
        self.right_motor.value = -speed

    def left(self, speed=1.0):
        self.left_motor.value = -speed
        self.right_motor.value = speed

    def right(self, speed=1.0):
        self.left_motor.value = speed
        self.right_motor.value = -speed

    def stop(self):
        self.left_motor.value = 0
        self.right_motor.value = 0


network = jetson.inference.detectNet(argv=['--model=/jetson-inference/python/training/detection/ssd/models/ssd-mobilenet.onnx', '--labels=/jetson-inference/python/training/detection/ssd/models/labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes'])

camera = jetson.utils.videoSource("/dev/video0") #change video device if necessary

display = jetson.utils.videoOutput()

robot = Robot()


i = ''
detectionTimer = 0
flag = 1
printFlag = 0
moneySum = 0
most_common_detection = 0


while True:		
	
	detectionList = []

	while detectionTimer <= 55: #to take the max present argument in 55 frames, approximately 1.5 seconds
		image = camera.Capture()
		detection = network.Detect(image)
		display.Render(image)	
		display.SetStatus("Object Detection | Network {:.0f} FPS".format(network.GetNetworkFPS()))

		try:
			detectionTimer += 1
			detectionList.append(detection[0].ClassID)
			most_common_detection = max(detectionList, key = detectionList.count)		

		except:
			detectionTimer += 1

	if int(most_common_detection) == 6 and flag == 1: 	# money is being put into moneybox
		i = 'putMoney'
		flag = 0
			
	elif int(most_common_detection) == 7 and flag == 1:   # money is being taken out of the moneybox
		i = 'takeMoney'
		flag = 0
		robot.left(speed=0.3)  # box's roof opens before money detection if money is being taken out of the moneybox
		time.sleep(1)
		robot.right(speed=0.3)
		time.sleep(1)
		robot.stop()

	if i == 'putMoney' and flag == 0:

		if int(most_common_detection) == 1: 
			moneySum += 5
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 2: 
			moneySum += 10
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 3:
			moneySum += 20
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 4:
			moneySum += 50
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 5:
			moneySum += 100
			flag = 1
			printFlag = 1

				
	elif i == 'takeMoney' and flag == 0:
				
		if int(most_common_detection) == 1: 
			moneySum -= 5
			flag = 1
			printFlag = 1
	

		elif int(most_common_detection) == 2: 
			moneySum -= 10
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 3:
			moneySum -= 20
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 4:
			moneySum -= 50
			flag = 1
			printFlag = 1


		elif int(most_common_detection) == 5:
			moneySum -= 100
			flag = 1
			printFlag = 1


	if printFlag == 1:
		print('moneySum:', moneySum)
		printFlag=0
		if i == 'putMoney': # box's roof opens after money detection if money is being put into moneybox
			robot.left(speed=0.3)
			time.sleep(1)
			robot.right(speed=0.3)
			time.sleep(1)
			robot.stop()

	detectionTimer = 0
	
	
