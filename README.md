# 🌱 GreenMind ML
### Intelligent Greenhouse Temperature Control System

**Arduino | Raspberry Pi 5 | Python | Machine Learning | Control Engineering**

GreenMind ML is an experimental engineering project combining embedded systems, electronics, control engineering, and machine learning.

The main objective is to investigate whether a machine-learning-assisted PI controller can improve temperature regulation compared with a conventional PID controller.

The project is based on a real, custom-built miniature greenhouse equipped with temperature sensors, a heating element, and a ventilation fan.

---

## Project Overview

The greenhouse consists of:

- **Arduino** — sensor readings and hardware control.
- **Raspberry Pi 5** — data processing, machine learning, and controller execution.
- **Two DHT11 temperature sensors** — measuring temperature at different heights.
- **12V incandescent bulb** — providing controllable heating through PWM.
- **12V fan** — providing on/off ventilation.
- **Python software** — implementing control algorithms and processing experimental data.

The system collects temperature measurements under different operating conditions. These measurements are used to train a machine learning model capable of predicting future temperature changes.

## Hardware Development

The physical system was designed, assembled, wired, and tested independently.

The work included:

- Building the miniature greenhouse.
- Integrating Arduino and Raspberry Pi 5.
- Connecting temperature sensors, heating, and ventilation.
- Implementing PWM heating control.
- Developing serial communication between Arduino and Raspberry Pi.
- Writing software for sensor readings and data collection.
- Conducting physical experiments and collecting measurements.

## Machine Learning

A supervised regression model was developed to predict greenhouse temperature 60 seconds into the future.

The machine learning workflow included:

- Collecting experimental temperature data.
- Preparing and preprocessing datasets using Python and Pandas.
- Dividing measurement batches into training and testing datasets.
- Performing group-based cross-validation.
- Training and evaluating regression models.
- Saving the trained model for practical use.
- Integrating temperature predictions into a PI-based control strategy.

The objective was not only to obtain accurate predictions but also to apply machine learning to a real physical control system.

## PID vs PI + ML

Two temperature control strategies were implemented and tested.

### 1. Conventional PID Controller

A traditional feedback controller using proportional, integral, and derivative terms to regulate the greenhouse temperature.

### 2. Machine-Learning-Assisted PI Controller

A PI controller enhanced with predictions from a trained machine learning model.

The prediction-based approach aims to improve temperature regulation by anticipating future changes in the system.

### Experimental Comparison

Both controllers were tested on the physical greenhouse with a target temperature of 30°C.

Initial results indicated that:

- The conventional PID controller reached the target temperature faster.
- The PI + ML controller achieved a smaller average temperature tracking error during the final stage of the experiment.
- The controllers exhibited different overshoot and temperature stability characteristics.

These are preliminary experimental results. Additional testing under controlled, repeatable conditions is necessary to establish broader performance conclusions.

## GreenMind ML Dashboard

The project includes a browser-based dashboard for visualizing and comparing the experimental results.

The dashboard provides:

- Animated temperature charts.
- PID vs PI + ML comparisons.
- Adjustable playback speed.
- Heating PWM visualization.
- Fan status monitoring.
- Temperature error analysis.
- Performance metrics and experiment summaries.

The dashboard replays recorded CSV measurements and does not directly control the physical greenhouse.

## Technologies

| Category | Technology |
|---|---|
| Programming | Python, Arduino C/C++ |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Hardware | Raspberry Pi 5, Arduino |
| Control Systems | PID, PI + ML |
| Communication | USB Serial |
| Data Storage | CSV |
| Visualization | HTML, CSS, JavaScript |
| Development Environment | VS Code, Linux |

## Photographs and Experimental Results

This repository includes photographs of the physical greenhouse, experimental datasets, temperature plots, and controller performance comparisons.

## Project Development and AI Transparency

**The GreenMind ML engineering project was independently developed by me.**

I personally worked on the physical construction, electronics integration, Arduino programming, Raspberry Pi communication, data collection, machine learning model development, controller implementation, and experimental evaluation.

**The only component whose code was created by AI rather than authored by me is the final web-based visualization dashboard (`dashboard.py`).**

The dashboard was added to present the experimental results in an interactive and accessible format.

The underlying control algorithms, machine learning experiments, hardware integration, and recorded measurements represent my own engineering work.

## Project Goals

GreenMind ML was developed to gain practical experience in:

- Machine learning applied to physical systems.
- Embedded programming and hardware integration.
- Classical and prediction-assisted control.
- Experimental data analysis.
- Designing and evaluating a complete engineering system.

---

**GreenMind ML — Connecting Machine Learning with Real-World Control Engineering.**
