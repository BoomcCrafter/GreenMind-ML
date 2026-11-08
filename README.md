# 🌱 GreenMind ML
### Intelligent Greenhouse Temperature Control System

**Arduino | Raspberry Pi 5 | Python | Machine Learning | Control Engineering**

GreenMind ML is an experimental engineering project combining embedded systems, electronics, classical control theory, and machine learning.

The main objective of the project is to investigate whether a **machine-learning-assisted PI controller can improve temperature regulation compared with a conventional PID controller**.

Unlike purely software-based simulations, GreenMind ML was developed using a real, custom-built miniature greenhouse. The system measures temperature, controls heating and ventilation, collects experimental data, and uses a trained machine learning model to predict future temperature changes.

The project demonstrates how machine learning can be integrated into a real physical control system.

---

## 1. Physical Greenhouse Prototype

The miniature greenhouse was physically built and equipped with an electronic temperature monitoring and control system.

### Hardware Gallery

| Greenhouse Prototype | Internal Construction |
|---|---|
| ![GreenMind ML prototype](images/model_1.jpg) | ![GreenMind ML hardware](images/model_2.jpg) |
| ![Greenhouse construction](images/model_3.jpg) | ![Greenhouse electronics](images/model_4.jpg) |

### Hardware Components

| Component | Function |
|---|---|
| Raspberry Pi 5 | Machine learning, data processing and controller execution |
| Arduino | Sensor acquisition and actuator control |
| 2 × DHT11 | Temperature measurement at different heights |
| 12V incandescent bulb | Heating element controlled using PWM |
| 12V fan | On/off ventilation |
| MOSFET | Electronic switching and PWM power control |
| USB Serial | Communication between Arduino and Raspberry Pi |

### Hardware Development

The physical greenhouse was designed, assembled, wired, and tested independently.

The development process included:

- Building the miniature experimental chamber.
- Installing temperature sensors in the upper and lower sections.
- Implementing PWM control of the heating element.
- Integrating an on/off ventilation fan.
- Establishing communication between Arduino and Raspberry Pi.
- Implementing sensor readings and data transmission.
- Testing the electrical system and its operation.
- Collecting temperature measurements during physical experiments.

The result is a working experimental platform for studying temperature dynamics and developing control algorithms.

---

## 2. System Operation

The system consists of two main computing devices with different responsibilities.

**Arduino — Hardware Layer**

Arduino is responsible for communicating with the physical components of the greenhouse.

Its main responsibilities include:

- Reading temperatures from both DHT11 sensors.
- Controlling heating power through PWM.
- Switching the ventilation fan.
- Sending measurement data to Raspberry Pi.
- Receiving control commands from Raspberry Pi.

**Raspberry Pi 5 — Control and Machine Learning Layer**

Raspberry Pi executes the software responsible for temperature regulation and analysis.

Its tasks include:

- Receiving measurements from Arduino.
- Processing temperature and control data.
- Executing the PID or PI + ML control algorithm.
- Loading and using the trained machine learning model.
- Calculating heating commands.
- Recording experimental results in CSV files.

The separation between hardware control and higher-level computation allows the system to combine embedded programming with machine learning.

---

## 3. Experimental Data Collection

Before implementing the machine learning controller, experimental measurements were collected to study how the greenhouse responds to different operating conditions.

The heating element was controlled using different PWM values, while the ventilation fan operated in defined on/off states.

The experiments were designed to observe the relationship between:

- Current temperature inside the greenhouse.
- Temperature at different sensor locations.
- Ambient temperature.
- Heating power.
- Ventilation state.
- Time and temperature changes.

The results were stored in CSV files for further processing in Python.

### Measurement Batches

Data was collected in separate measurement batches representing individual experiments.

This organization is important because consecutive temperature measurements from one experiment are strongly related to each other.

Separating entire measurement batches during model evaluation helps reduce data leakage and provides a more realistic assessment of performance on unseen experiments.

---

## 4. Machine Learning Model

One of the main objectives of GreenMind ML was to develop a machine learning model capable of predicting future greenhouse temperature.

The model uses experimental measurements to estimate the expected temperature behavior approximately **60 seconds ahead**.

### Machine Learning Workflow

The development process included:

1. Collecting experimental measurements from the physical greenhouse.
2. Loading and processing CSV datasets using Pandas.
3. Preparing input features and prediction targets.
4. Organizing measurements into experimental batches.
5. Training and validating regression models.
6. Evaluating prediction accuracy.
7. Saving the trained model using Joblib.
8. Integrating the trained model into the temperature control algorithm.

### Why Predict Future Temperature?

A conventional feedback controller reacts to the current temperature error.

However, a greenhouse has thermal inertia.

Even after heating power is reduced, the temperature may continue increasing because heat has already accumulated inside the system.

Machine learning can provide information about the expected future temperature.

This enables the controller to consider not only the current temperature but also its predicted evolution.

The objective is to improve regulation by anticipating temperature changes rather than reacting only after they occur.

---

## 5. Temperature Control Algorithms

Two different control strategies were implemented and experimentally evaluated.

### 5.1 Conventional PID Controller

The classical PID controller uses three components:

**Proportional (P)**

Responds to the current difference between the target temperature and the measured temperature.

**Integral (I)**

Accumulates the temperature error over time and helps eliminate persistent steady-state error.

**Derivative (D)**

Responds to changes in error and can help reduce overshoot.

The PID controller calculates the heating command based on these components.

### 5.2 Machine-Learning-Assisted PI Controller

The second approach combines a PI controller with a machine learning prediction model.

The PI controller provides conventional feedback regulation, while the machine learning model estimates future temperature behavior.

The prediction is incorporated into the control strategy to help anticipate thermal changes.

This approach was developed to investigate whether additional predictive information can improve temperature tracking and reduce excessive heating.

The objective is not to replace classical control theory but to explore how it can be enhanced with machine learning.

---

## 6. Experimental Comparison — PID vs PI + ML

Both controllers were tested using the physical greenhouse.

The target temperature during the comparison experiments was **30°C**.

The recorded measurements were used to evaluate several aspects of control performance:

- Time required to approach the target temperature.
- Temperature tracking accuracy.
- Maximum temperature overshoot.
- Temperature fluctuations.
- Heating PWM behavior.
- Stability during the final stage of regulation.

### Experimental Charts

The following charts present recorded experimental results and visual comparisons between the two control strategies.

![GreenMind ML experimental plot 1](images/plot_1.png)

![GreenMind ML experimental plot 2](images/plot_2.png)

![GreenMind ML experimental plot 3](images/plot_3.png)

![GreenMind ML experimental plot 4](images/plot_4.png)

### Initial Observations

The initial experiments revealed differences between the two controllers.

**Conventional PID:**

- Reached the target temperature region faster.
- Exhibited higher temperature overshoot.
- Demonstrated relatively stable behavior during the final stage of regulation.

**PI + Machine Learning:**

- Approached the target temperature more gradually.
- Exhibited lower overshoot in the recorded comparison.
- Achieved a smaller average temperature tracking error during the final stage.
- Demonstrated the potential benefits of prediction-assisted temperature control.

### Important Limitations

The comparison is based on recorded physical experiments.

Differences in initial and environmental conditions can influence the results.

Therefore, these observations should not be interpreted as proof that machine learning is universally better than classical PID control.

Additional repeated experiments under comparable conditions would be required for a more reliable comparison.

---

## 7. GreenMind ML — Interactive Dashboard

A dedicated browser-based dashboard was developed to visualize and compare the experimental results.

The dashboard makes the project easier to understand and allows users to explore the differences between the two control strategies.

### Dashboard Features

- Interactive temperature visualization.
- Animated playback of recorded measurements.
- Side-by-side PID and PI + ML comparison.
- Adjustable playback speed.
- Heating PWM visualization.
- Fan operating state.
- Temperature readings from individual sensors.
- Temperature tracking error analysis.
- Performance metrics and experiment summaries.

The dashboard reads recorded CSV measurements.

**It does not directly control the physical greenhouse or run a new physical experiment.**

The dashboard can be launched independently of the hardware, allowing other users to explore the recorded results on their own computers.

---

## 8. Video Demonstration

A short video demonstrates the physical GreenMind ML prototype and its operation.

### Watch the Prototype in Action

**🎬 [Watch the GreenMind ML Demonstration (MP4)](videos/video.mp4)**

The recording provides a practical look at the system developed for the experiment.

---

## 9. Technologies and Tools

| Category | Technologies |
|---|---|
| Programming | Python, Arduino C/C++ |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Hardware | Raspberry Pi 5, Arduino |
| Control Engineering | PID, PI + ML |
| Model Serialization | Joblib |
| Communication | USB Serial |
| Data Storage | CSV |
| Web Dashboard | HTML, CSS, JavaScript, Python |
| Development Environment | Visual Studio Code, Linux |

---

## 10. Project Development and AI Transparency

**GreenMind ML is an independently developed engineering project.**

I personally worked on:

- Physical greenhouse design and construction.
- Electronics assembly and hardware integration.
- Arduino programming.
- Raspberry Pi communication.
- Experimental data collection.
- Data preparation and machine learning model development.
- Implementation of the control algorithms.
- Integration of machine learning with temperature regulation.
- Physical testing and experimental evaluation.

### AI-Assisted Component

**The only component whose code was generated by AI rather than written by me is the final web-based visualization dashboard (`dashboard.py`).**

This component was added to provide an accessible and interactive presentation of the experimental results.

The underlying machine learning experiments, controllers, hardware integration, and physical measurements represent my own engineering work.

---

## 11. Project Objectives and Learning Outcomes

GreenMind ML was created as a practical engineering project focused on combining software, electronics, automation, and artificial intelligence.

The main goals were to:

- Understand the dynamics of a real thermal system.
- Learn how to collect and analyze physical sensor data.
- Apply supervised machine learning to temperature prediction.
- Implement classical and prediction-assisted controllers.
- Integrate Arduino with Raspberry Pi.
- Evaluate control performance through experiments.
- Build a complete hardware-software system.

The project demonstrates the practical application of machine learning in control engineering, rather than using machine learning only for offline data analysis.

---

### 🌱 GreenMind ML

**Exploring the connection between Machine Learning, Embedded Systems and Real-World Control Engineering.**
