Marathoner
==========

Marathoner is a command line tool for effective local testing of solutions for [Marathon Match competitions](http://community.topcoder.com/longcontest/?module=ViewActiveContests) organized by [TopCoder Inc.](http://www.topcoder.com/)
It works directly with visualizer .jar files (provided by TopCoder), so it doesn't require any changes to the solution code.

Features
--------

- Cross-platform: Windows, Linux, OSX. Written in Python.
- VERY simple interface.
  To run your solution on seed 5 just type: ```5```
  To run your solution on first 100 seeds, just type: ```1 100```
- Keeping track of the best scores for each test case, so you can compare your solutions locally.
- Export of input data from visualizer into file, so you can debug on them.


Installation
------------

Get Python 2.6 or 2.7 at [http://www.python.org](http://www.python.org).

Install it as any other Python library. Either run ```pip install marathoner```
or download the source code and run ```python setup.py install```.


Getting started
---------------

Let me show you how to setup Marathoner for a recent Marathon Match [ColorLinker](http://community.topcoder.com/longcontest/?module=ViewProblemStatement&compid=34370&rd=15825)

1. Download the visualizer [ColorLinkerVis.jar](http://www.topcoder.com/contest/problem/ColorLinker/v2/ColorLinkerVis.jar).
   Create a solution that communicates with visualizer as described [here](http://apps.topcoder.com/forums/?module=Thread&threadID=670892&start=0)
   and make sure your solution works by running: ```java -jar ColorLinkerVis.jar -exec "<command>" -seed 1```

2. In your working directory run ```marathoner new ColorLinkerMrtn```.

   Marathoner will create a new directory named *ColorLinkerMrtn* where it will
   store all files and folders related to ColorLinker match.

3. Go into newly created directory *ColorLinkerMrtn* and edit *marathoner.cfg* file.
   Fill out its contents as described in comments inside the file. Here is an example of my .cfg file for this match:

   ```
   [marathoner]
   visualizer = c:\Users\Mimino\Documents\Visual Studio 2010\Projects\ColorLinker\ColorLinkerVis.jar
   solution = c:\Users\Mimino\Documents\Visual Studio 2010\Projects\ColorLinker\Release\ColorLinker.exe
   source = c:\Users\Mimino\Documents\Visual Studio 2010\Projects\ColorLinker\ColorLinker\ColorLinker.cpp
   testcase = c:\Users\Mimino\Documents\Visual Studio 2010\Projects\ColorLinker\testcase.txt
   maximize = false
   novis = -novis
   vis =
   params = -side 10
   ```

4. While still in *ColorLinkerMrtn* directory, run ```marathoner run```.
   If everything is okay, you should see a welcome message and the command line prompt. Try typing:
   ```
   >>> 1
   ```
   You should see the visualizer running for the seed number 1.
   Congratulations, you are now ready to compete!
