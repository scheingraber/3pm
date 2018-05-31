# Personal Pomodoro Productivity Manager (3PM)
----------------------------------------------

## Introduction
Personal Pomodoro Productivity Manager (3PM) is a task-based productivity timer. It furthermore allows to simulate the likely completion of a task using the accuracy of earlier estimates.

Find out more on the [official website](https://chrispara.github.io/3pm/)!

## Theoretical Background
The idea that productivity can best be maintained maintained with highly concentrated work sessions which are interrupted by short breaks is the basis of the [pomodoro technique](https://en.wikipedia.org/wiki/Pomodoro_Technique).
3PM is a task list and pomodoro timer. The completion probability of tasks is simulated lending some ideas from [Evidence-based scheduling](https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/) (Cumulative Distribution Function of completion date, obtained using Monte-Carlo Simulation).

## 3PM in Action
![](src/data/demo.gif)

## Installation
### Windows
You can use the provided self-extracting archive from [Github releases](https://github.com/ChrisPara/3pm/releases).

### Android
Use the provided apk from [Github releases](https://github.com/ChrisPara/3pm/releases).

### Linux
Dependencies:

* python=2.7
* docutils
* pygments
* kivy
* plyer<1.3.0

Install 3PM using virtualenv and pip:
```bash
virtualenv 3pm_env
source 3pm_env/bin/activate
pip install --upgrade pip wheel setuptools
pip install docutils pygments
pip install kivy
pip install 'plyer<1.3.0'
git clone https://github.com/ChrisPara/3pm
python 3pm/src/main.py
```

### macOS and iOS
Should work just fine on macOS using the steps for Linux, but this has not been tested. An iOS package will be provided in the near future.
