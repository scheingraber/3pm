# PyPomoProjectManager (3pm)
-----------------------------

##Info
PyPomoProjectManager (3pm) is a basic project manager:
* project-based todo-lists
* pomodoro timer

##Todo
* evidence-based project scheduler

The idea is to combine todo-items into projects and perform [Pomodoro timer sessions](http://cirillocompany.de/pages/pomodoro-technique) for these todo-items.
The estimated time versus actual completion time are used to obtain a velocity rating.
The completion of projects can then be visualized using the idea of [Evidence-based scheduling](https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/) (Cumulative Distribution Function of completion date, obtained using Monte-Carlo Simulation).

##Install
### Windows
On Windows, you can use the provided installer, see the Github releases page.

### Android
Copy src dir to sdcard/kivy and use the Kivy-Lancher app. An apkg will be provided in the near future.

### Linux
Python 2.7 or 3.5 are supported. You need the following PIP packages:
* docutils
* pygments
* pypiwin32
* kivy.deps.sdl2
* kivy.deps.glew
* kivy

E.g., using Anaconda and pip:
```bash
conda create -n 3pm python=2.7
source activate 3pm
python -m pip install --upgrade pip wheel setuptools
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy
git clone https://github.com/ChrisPara/3pm
python 3pm/src/main.py
```

### OSX
Supported, but you have to install Python and kivy.
