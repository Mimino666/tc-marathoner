Marathoner
==========

Marathoner is a command line tool for effective local testing of solutions for [Marathon Match competitions](http://community.topcoder.com/longcontest/?module=ViewActiveContests) organized by [TopCoder Inc.](http://www.topcoder.com/)


Features
--------

- Cross-platform: Windows, Linux, Mac OS X. Written in Python.
- Works with visualizer .jar files, so it doesn't require any changes to your solution code.
- VERY simple interface.
  To run your solution on seed 5 just type: ```5```.
  To run your solution on first 100 seeds, just type: ```1 100```.
- Keeps track of the best scores for each seed, so you can compare your solutions locally.
- Exports input data from visualizer into file, so you can debug on them.


Installation
------------

Get Python at [http://www.python.org](http://www.python.org) (versions 2.6, 2.7 and 3.x are supported).

If you have *pip* Python package manager installed, run: ```pip install marathoner```. To upgrade for a newer version, run: ```pip install marathoner --upgrade```.

Or download the source code from GitHub and from *tc-marathoner* directory run: ```python setup.py install```.


Getting started
---------------

Let me show you how to setup Marathoner for a recent Marathon Match called [ColorLinker](http://community.topcoder.com/longcontest/?module=ViewProblemStatement&compid=34370&rd=15825).

1. Download the visualizer [ColorLinkerVis.jar](http://www.topcoder.com/contest/problem/ColorLinker/v2/ColorLinkerVis.jar).
   Create a solution that communicates with visualizer as described [here](http://apps.topcoder.com/forums/?module=Thread&threadID=670892&start=0)
   and make sure your solution works by running: ```java -jar ColorLinkerVis.jar -exec "<command>" -seed 1```

2. From command line run: ```marathoner new ColorLinkerMarat```.

   In your current directory Marathoner will create a new directory named *ColorLinkerMarat* where it will
   store all its work files related to ColorLinker match.

3. Go into newly created directory *ColorLinkerMarat* and edit *marathoner.cfg* file.
   Fill out its contents as described in comments inside the file. Here is an example of my *marathoner.cfg* file for this match:

   ```
   [marathoner]
   visualizer = c:\Users\Mimino\ColorLinker\ColorLinkerVis.jar
   solution = "c:\Users\Mimino\ColorLinker\ColorLinker.exe"
   source = c:\Users\Mimino\ColorLinker\ColorLinker.cpp
   testcase = c:\Users\Mimino\ColorLinker\testcase.txt
   maximize = false
   novis = -novis
   vis =
   params = -side 10
   ```

4. While still in *ColorLinkerMarat* directory, from command line run: ```marathoner run```.
   If everything is okay, you should see a welcome message and the command line prompt. Try to run:
   ```
   >>> 1
   Running single test 1...
   Score = 123456.0
           Run time: 0.14
           New score: 1234567.00
           Best score: 123456.00
           Relative score: 0.09999
   ```
   You should also see the visualization for the seed number 1. Close the visualizer and type another command.

Congratulations, you are now ready to compete!


Basic commands
--------------

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
>>> best 1 100          # print the best scores for seeds from interval 1-100, inclusive
```

#### clear
Clear console window.

#### help
Show list of available commands.

#### quit
Quit Marathoner prompt.


Tagging of solutions
--------------------

Once you have implemented a solution that you plan to run on a large number
of tests you can *tag* the solution, before you do so:
```
>>> tag create my_solution             # tag the current solution with name "my_solution"
```
Marathoner will compute the hash of your current source code (you specified path to your source code in .cfg file)
and store it under the name "*my_solution*". Now whenever you run some tests,
Marathoner will check the hash of your current source code against the hashes
of the source codes that you have already tagged. If there is a match, Marathoner will
store the results of the tests under the matched tag name.
```
>>> tag                                 # display the list of existing tags
|-----------------|---------------------|
|             Tag |             Created |
|-----------------|---------------------|
| (*) my_solution | 2013-12-13 04:26:54 |
|-----------------|---------------------|
(*) means current active tag
>>> 1 100                               # run seeds 1-100 and store the scores under "my_solution" tag
Running 100 tests with tag "my_solution"...
>>> 101 200                             # run seeds 101-200 and add them to "my_solution" tag
Running 100 tests with tag "my_solution"...
>>> tag cmp my_solution                 # view the scores of seeds 1-200 of "my_solution" tag
```
And now comes the killer! When you have tagged many different solutions
and you want to compare them against each other, simply run the command:
```
>>> tag cmp my_solution other_solution  # compare the scores of tags "my_solution" and "other_solution"
```

Note: Be careful when you change the source code of your solution and don't compile it.
Marathoner will still run the old code, but the hash of the source file will be different.


#### tag
Print the list of existing tags. Examples:
```
>>> tag
|---------------|---------------------|
|           Tag |             Created |
|---------------|---------------------|
| (*) solution1 | 2013-12-13 04:26:54 |
|     solution2 | 2013-12-13 01:14:32 |
|---------------|---------------------|
(*) means current active tag
```

#### tag create &lt;tag&gt;
Tag the current solution with the given name. Examples:
```
>>> tag create solution1                # tag the current solution with name "solution1"
>>> 1 10                                # run the seeds 1-10 and store them under "solution1" tag
Running 10 tests with tag "solution1"...

( change source code of solution )
>>> 1 10                                # now, because the source code has changed, the current solution doesn't have any tag
Running 10 tests...

( change source code back )             # Marathoner automatically detects the change and "solution1" tag is active again
>>> 11 20                               # run the seeds 11-20 and store them under "solution1" tag
Running 10 tests with tag "solution1"...
```

#### tag delete &lt;tag&gt;
Delete the selected tag. Examples:
```
>>> tag delete solution1
Are you sure you want to delete tag "solution1"? [y/n]  y
Tag "solution1" was deleted.
```

#### tag cmp &lt;tag1&gt; &lt;tag2&gt; ...
Compare the scores of the selected tags. Only the seeds that all the tags have in common will be compared. Examples:
```
>>> tag create solution1              # create tag "solution1"
>>> 1 10                              # run the seeds 1-10 and store them under "solution1" tag
>>> tag cmp solution1                 # view the scores of solution1 on seeds 1-10

( change source code of solution )
>>> tag create solution2              # create tag "solution2"
>>> 5 15                              # run the seeds 5-15 and store them under "solution2" tag
>>> tag cmp solution1 solution2       # compare the score of solutions on seeds 5-10 (these are the seeds they have in common)

( chagnge source code again )
>>> tag create solution3              # create tag "solution3"
>>> 9 10                              # run the seeds 9-10 and store them under "solution3" tag
>>> tag cmp solution1 solution2 solution3  # compare the score of solutions on seeds 9-10
```


Tips and tricks
---------------

- If your solution gets stuck, press ```q``` to easily terminate it. If you are running multiple tests, it terminates the whole execution (best scores of already run tests are still saved, though).
- If your solution crashes on some seed and you want to debug it, you can find input data of this seed in file specified by *testcase* field in *marathoner.cfg*.
- You can find log of the last multiple-tests run in *ColorLinkerMarat* directory, called *multiple_tests.log*.
- When you run multiple tests, standard error output from your solution is not displayed. But lines starting with ```!``` are displayed, still.
- Marathoner stores copies of all tagged source codes in ```ColorLinkerMarat/tags``` directory, so you can later return to them.
- If you internally measure running time of your solution, output to standard error a line in format: ```Run time = <run_time>```. Marathoner will use this time instead of the one it measures externally, which is not entirely precise.
