Marathoner
==========

Marathoner is a command line tool for effective local testing of solutions for [Marathon Match competitions](http://community.topcoder.com/longcontest/?module=ViewActiveContests) organized by [TopCoder Inc.](http://www.topcoder.com/)


Features
--------

- Cross-platform: Windows, Linux, Mac OS X. Written in Python.
- VERY simple interface.
  To run your solution on seed 5 just type: ```5```.
  To run your solution on first 100 seeds, just type: ```1 100```.
- Keeping track of the best scores for each seed, so you can compare your solutions locally.
- Export of input data from visualizer into file, so you can debug on them.
- Works with visualizer .jar files, so it doesn't require any changes to the solution code.


Installation
------------

Get Python at [http://www.python.org](http://www.python.org) (versions 2.6, 2.7 and 3.x are supported).

If you have *pip* Python package manager installed, run: ```pip install marathoner```.

Or download the source code and from *marathoner* directory run: ```python setup.py install```.


Getting started
---------------

Let me show you how to setup Marathoner for a recent Marathon Match called [ColorLinker](http://community.topcoder.com/longcontest/?module=ViewProblemStatement&compid=34370&rd=15825).

1. Download the visualizer [ColorLinkerVis.jar](http://www.topcoder.com/contest/problem/ColorLinker/v2/ColorLinkerVis.jar).
   Create a solution that communicates with visualizer as described [here](http://apps.topcoder.com/forums/?module=Thread&threadID=670892&start=0)
   and make sure your solution works by running: ```java -jar ColorLinkerVis.jar -exec "<command>" -seed 1```

2. From command line run: ```marathoner new ColorLinkerMarat```.

   In your current directory Marathoner will create a new directory named *ColorLinkerMarat* where it will
   store all files and folders related to ColorLinker match.

3. Go into newly created directory *ColorLinkerMarat* and edit *marathoner.cfg* file.
   Fill out its contents as described in comments inside the file. Here is an example of my .cfg file for this match:

   ```
   [marathoner]
   visualizer = c:\Users\Mimino\ColorLinker\ColorLinkerVis.jar
   solution = "c:\Users\Mimino\ColorLinker\ColorLinker.exe"  # notice the quotes here!
   # for Java:
   #   solution = java -cp "c:\Users\Mimino\ColorLinker\ColorLinker.class"
   source = c:\Users\Mimino\ColorLinker\ColorLinker\ColorLinker.cpp
   testcase = c:\Users\Mimino\ColorLinker\testcase.txt
   maximize = false
   novis = -novis
   vis =
   params = -side 10
   ```

4. While still in *ColorLinkerMarat* directory, from command line run: ```marathoner run```.
   If everything is okay, you should see a welcome message and the command line prompt. Try typing:
   ```
   >>> 1
   Running single test 1...
   Score = 123456.0
           Run time: 0.146289
           New score: 1234567.000000
           Best score: 123456.000000
           Relative score: 0.0999994
   ```
   You should see the visualization for the seed number 1. Close the visualizer and type another command.

   Congratulations, you are now ready to compete!


Available commands
------------------

#### &lt;seed&gt; [vis params]
Run single test with visualization. Examples:
```
>>> 5                   # run seed 5
>>> 5 -side 15          # run seed 5 with additional visualizer option "-side 15"
```

#### &lt;seed1&gt; &lt;seed2&gt; [vis params]
Run multiple tests with seeds from interval *seed1*-*seed2*, inclusive. Visualization is turned off. Examples:
```
>>> 1 100               # run seeds from interval 1-100, inclusive
>>> 1 100 -side 15      # run seeds from interval 1-100, inclusive, with additional visualizer option "-side 15"
```

#### best [seed1] [seed2]
Print the best scores for the seeds. Examples:
```
>>> best                # print the best scores for all the known seeds
>>> best 5              # print the best score for seed 5
>>> best 1 100          # print the best scores for seeds in interval 1-100, inclusive
```

#### clear
Clear console window.

#### help
Show list of available commands.

#### quit
Quit Marathoner prompt.


Tips and tricks
---------------

- If your solution gets stuck, type "*Q*" to terminate its execution. If you are executing multiple tests, it terminates the whole execution.
- If your solution crashes on some seed and you want to debug it, you can find input data of this seed in file specified by *testcase* field in the .cfg file.
- If you internally measure running time of your solution, from your solution output to standard error line in format: "```Run time = <run_time>```" and Marathoner will parse it out for further processing.
- You can find log of the last multiple-tests run in *ColorLinkerMarat* dictionary, called *multiple_tests.log*.
- When you run multiple tests, standard error output from your solution is not displayed. But lines starting with "!" are displayed, still.
