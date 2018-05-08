# PyPomoProjectManager (3pm)
-----------------------------

### Info
PyPomoProjectManager (3pm) is a basic project manager:
* project-based todo-lists
* pomodoro timer

### Todo
* evidence-based project scheduler

The idea is to combine todo-items into projects and perform [Pomodoro timer sessions](http://cirillocompany.de/pages/pomodoro-technique) for these todo-items.
The estimated time versus actual completion time are used to obtain a velocity rating.
The completion of projects can then be visualized using the idea of [Evidence-based scheduling](https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/) (Cumulative Distribution Function of completion date, obtained using Monte-Carlo Simulation).

## Install
### Windows
You can use the provided self-extracting archive from [Github releases](https://github.com/ChrisPara/3pm/releases).

### Android
Use the provided apk from [Github releases](https://github.com/ChrisPara/3pm/releases).

### Linux
Install dependencies:
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

### OSX and IOS
Not tested, but should work just fine.
