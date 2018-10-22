# Personal Pomodoro Productivity Manager (3PM)
----------------------------------------------

## Introduction
Personal Pomodoro Productivity Manager (3PM) is a task-based productivity timer. It furthermore allows to simulate the likely completion of a task using the accuracy of earlier estimates.


## Theoretical Background
The idea that productivity can best be maintained maintained with highly concentrated work sessions which are interrupted by short breaks is the basis of the [pomodoro technique](https://en.wikipedia.org/wiki/Pomodoro_Technique).
3PM is a task list and pomodoro timer. The completion probability of tasks is simulated lending some ideas from [Evidence-based scheduling](https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/) (Cumulative Distribution Function of completion date, obtained using Monte-Carlo Simulation).

## Usage
    - add tasks you want to work on
    - you can enter a title and note for each task
    - enter the number of sessions you plan to spend on each task
    - click 'Start' and start working until the session is over
    - take a short break and repeat
    - when you are finished with a task click 'Finished'
    - for each finished task, 3PM learns a velocity rating
      (the ratio of your actually needed to planned sessions)
    - for new tasks, you get a probability distribution based on your old ratings
      (in the lower right, corresponding to 25%,50%,75%,100% quantiles)
    - this tells you how many sessions you will at most need
      (with the corresponding probability)

## 3PM in Action
![](src/data/demo.gif)

Find out more on the [official website](https://scheingraber.github.io/3pm/)!

## Installation
### Windows
You can use the provided *exe* (self-extracting archive) from [Github releases](https://github.com/scheingraber/3pm/releases).

### Android
Use the provided *apk* from [Github releases](https://github.com/scheingraber/3pm/releases).

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
git clone https://github.com/scheingraber/3pm
python 3pm/src/main.py
```

### macOS
Use the provided *dmg* from [Github releases](https://github.com/scheingraber/3pm/releases).

## iOS
An iOS package will be provided in the near future.
