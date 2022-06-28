# zq-forcing-game

## Introduction
This repository contains a pygame program that can be used to play out the Z_q forcing game on a graph as described in [this paper](https://journals.uwyo.edu/index.php/ela/article/download/1501/1501/)

## Installation
Get all of these files into a folder on your computer somehow. The recommended method is to [install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and then run this command inside your target folder:
```
git clone https://github.com/chostetler/zq-forcing-game.git
```
You will also need to [install python](https://www.python.org/downloads/)

__Recommended__ - set up a virtual environment.

First, install virtualenv:
```
pip install virtualenv
```

Then, create and activate the environment:

Windows
```
python -m venv venv
```
```
.\venv\Scripts\activate
```

Mac/Linux
```
python -m venv venv
```
```
source venv/bin/activate
```

__Required__ - install requirements and run
```
pip install -r requirements.txt
```
```
python src/main.py
```

