# Intelligent Moneybox with Object Detection
## Motivation
Children are imposed to save money and stop spending their money for unuseful products. They are given a moneybox and taught to save their money and hold them in their given moneyboxes. This is an appropriate approach to saving money. However, when time comes to summing up and declaring their total "wealth", things get a bit complicated. There can be various kinds of money magnitudes such as $5, $10... Grouping them, counting them, adding them up can be time consuming, and to be honest, a bit boring. Intelligent Moneybox can help solving this issue! 
## Project
### Peripheral Devices
- Logitech C270 Webcam
- DC Motor and a Tire
- Stepper FeatherWing Motor Driver
- A Box
### How Does It Work?
Model dataset has been collected manually (5-10-20-50-100 Turkish Liras and 2 hand gestures to identify the money's situation whether it is getting in the money box or getting out from it). I have used the widget that has been created by the [Jetson-inference](https://github.com/dusty-nv/jetson-inference) library. The widget can be used from [here](https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-collect-detection.md). Also, the training script is present in the [same page](https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-collect-detection.md). 
