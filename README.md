Marathoner
==========

Marathoner is a command line tool for effective local testing of solutions for [Marathon Match competitions](http://community.topcoder.com/longcontest/?module=ViewActiveContests) organized by [TopCoder Inc.](http://www.topcoder.com/)

Created with love by [Mimino](http://community.topcoder.com/tc?module=MemberProfile&cr=22685656).

Table of contents:

- [Features](https://github.com/Mimino666/tc-marathoner#features)
- [Installation](https://github.com/Mimino666/tc-marathoner#installation)
- [Getting started](https://github.com/Mimino666/tc-marathoner#getting-started)
- [Basic commands](https://github.com/Mimino666/tc-marathoner#basic-commands)
- [Tagging of solutions](https://github.com/Mimino666/tc-marathoner#tagging-of-solutions)
- [Tips and tricks](https://github.com/Mimino666/tc-marathoner#tips-and-tricks)


Features
--------

- Works with solutions written in C++, C#, Java, Python, VB.
- Provides a simple way to run your solution on multiple test cases.
  To run on the first hundred seeds, just type to command line prompt: ```1 100```.
- Keeps track of the best scores for each seed, so you can compare your solutions locally.
- Exports input data from visualizer into external file, so you can debug on them.
- Automatically versions your source code, so you can return to your previous solutions.
- (**NEW**) Caches the output of your solution, so you don't have to wait again when running the same code on the same seed.
- and many more...


Installation
------------

Marathoner is written in Python, so first get some Python at [http://www.python.org](http://www.python.org) (versions 2.6, 2.7 and 3.x are supported).

If you have *pip* (Python package manager) installed, run: ```$ pip install marathoner```.

To update Marathoner to newer version, run: ```$ pip install marathoner --upgrade```.

Or download the source code from GitHub and from *tc-marathoner* directory run: ```$ python setup.py install```.


Getting started
---------------

Let me show you how to setup Marathoner for a recent Marathon Match called [SmallPolygons](http://community.topcoder.com/longcontest/?module=ViewProblemStatement&compid=47276&rd=16445).

1. Download the visualizer [tester.jar](http://www.topcoder.com/contest/problem/SmallPolygons/tester.jar).
   Create a solution that communicates with visualizer as described [here](http://www.topcoder.com/contest/problem/SmallPolygons/manual.html)
   and make sure your solution works by running:

   ```$ java -jar tester.jar -exec "<command>" -seed 1```

2. Run from the command line: ```$ marathoner new SmallPolygonsMarat```

   Marathoner will create in the current directory a new project directory named *SmallPolygonsMarat*,
   where it will store all the files related to SmallPolygons match.

3. Go into newly created project directory and edit *marathoner.cfg* file.
   Fill out its contents as described in the comments inside the file.
   Here is an example of my *marathoner.cfg* file for this match:

   ```
   [marathoner]
   visualizer = c:\Mimino\SmallPolygons\tester.jar
   solution = "c:\Mimino\SmallPolygons\SmallPolygons.exe"
   source = c:\Mimino\SmallPolygons\SmallPolygons.cpp
   testcase = c:\Mimino\SmallPolygons\testcase.txt
   maximize = false
   novis =
   vis = -vis
   params = -debug
   cache = true
   ```

   Save and close the file.

4. While still in the project directory, run from the command line: ```$ marathoner run```.

   If everything is setup correctly, you should see a welcome message and the command line prompt. Try to run:
   ```
   >>> 1
   Running single test 1...
   Score = 123456.0
           Run time: 0.14
           New score: 1234567.00
           Best score: 123456.00
           Relative score: 0.09999
   ```
   You should also see the visualization for the seed number 1.

   Close the visualizer and type command ```help``` to show the list of available commands.

Congratulations, you are now ready to compete!


Basic commands
--------------

#### &lt;seed&gt; [&lt;vis params&gt;]
Run single test with visualization. Examples:
```
>>> 5                   # run seed 5
>>> 5 -nostrict         # run seed 5 with additional visualizer option "-nostrict"
```

#### &lt;seed1&gt; &lt;seed2&gt; [&lt;vis params&gt;]
Run multiple tests with seeds from interval *seed1*-*seed2*, inclusive. Visualization is turned off. Examples:
```
>>> 1 100               # run seeds from interval 1-100, inclusive
>>> 1 100 -nostrict     # run seeds from interval 1-100, inclusive, with additional visualizer option "-nostrict"
```

#### best [&lt;seed1&gt;] [&lt;seed2&gt;]
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

Once you have implemented a solution which you plan to run on a large number of tests,
you can *tag* the solution:
```
>>> tag create solution1                # tag the current solution with name "solution1"
```
Marathoner will compute the hash of your current source code (you specified path to your source code in .cfg file)
and store it under the name *solution1*. Now whenever you run some tests,
Marathoner will check the hash of your current source code against the hashes of the source codes you have already tagged.
If it finds the match, Marathoner will store the results of the tests under the matched tag.
```
>>> tag                                 # display the list of existing tags
|-----------------|-------|-------------|---------------------|
|             Tag | Seeds |  Avg. score |             Created |
|-----------------|-------|-------------|---------------------|
| (*) solution1   |     0 |    (!)  0.0 | 2013-12-13 04:26:54 |
|-----------------|-------|-------------|---------------------|

(*) means current active tag
(!) means the best average relative score

>>> 1 100                               # run seeds 1-100 and store the scores under "solution1" tag
Running 100 tests with tag "solution1"...

>>> 101 200                             # run seeds 101-200 and add them to "solution1" tag
Running 100 tests with tag "solution1"...

>>> tag
|-----------------|-------|-------------|---------------------|
|             Tag | Seeds |  Avg. score |             Created |
|-----------------|-------|-------------|---------------------|
| (*) solution1   |   200 |    (!)  1.0 | 2013-12-13 04:26:54 |
|-----------------|-------|-------------|---------------------|

(*) means current active tag
(!) means the best average relative score

>>> tag solution1                       # view the detail scores of seeds 1-200 of "solution1" tag
|------|---------|---------|----------|----------|
| Seed |   Score |    Best | Relative | Run time |
|------|---------|---------|----------|----------|
|    1 |   10.00 |   10.00 |    1.000 |     2.95 |
|    2 |  385.00 |  385.00 |    1.000 |     2.95 |
...
|  200 |  123.00 |  123.00 |    1.000 |     2.95 |
|------|---------|---------|----------|----------|

Relative score of "ch21" tag on 200 tests: 200.00
Average relative score: 1.00
```

And now comes the killer! When you have tagged many different solutions
and you want to compare them against each other, simply run the command:
```
>>> tag solution1 solution2             # compare the scores of tags "solution1" and "solution2"
|----------|-------------|-------------|---------|
|     Seed |   solution1 |   solution2 |    Best |
|----------|-------------|-------------|---------|
|        1 |   (+) 10.00 |        9.00 |   10.00 |
|        2 |  (*) 385.00 |  (*) 385.00 |  384.00 |
...
|      200 |      121.00 |  (+) 123.00 |  123.00 |
|----------|-------------|-------------|---------|
| Relative |   199.66398 |   199.58193 |     200 |
|  Average |     0.99831 |     0.99790 |    1.00 |
|    # (*) |          67 |          55 |       / |
|    # (+) |          34 |          30 |       / |
|----------|-------------|-------------|---------|

(*) means the best score among the selected tags
(+) means the absolute best score
```

**WARNING**: When you change the source code of your solution and don't compile it,
Marathoner will still run the old solution, but the hash of the source file will be different.
So it is possible that the solution will not run with the correct tag name.


#### tag
Print the list of existing tags. Examples:
```
>>> tag
|-----------------|-------|-------------|---------------------|
|             Tag | Seeds |  Avg. score |             Created |
|-----------------|-------|-------------|---------------------|
|     solution1   |   100 |         0.3 | 2013-12-13 03:00:00 |
| (*) solution2   |   200 |    (!)  1.0 | 2013-12-13 04:26:54 |
|-----------------|-------|-------------|---------------------|

(*) means current active tag
(!) means the best average relative score
```

#### tag &lt;tag_name&gt;
Print the scores of the selected tag. Examples:
```
>>> tag solution1
|------|----------|----------|----------|----------|
| Seed |    Score |     Best | Relative | Run time |
|------|----------|----------|----------|----------|
|    1 |   257.00 |   257.00 |    1.000 |     1.31 |
|    2 |   353.00 |   352.00 |    0.997 |     1.00 |
|    3 |     0.00 |   294.00 |    0.000 |     1.04 |
|------|----------|----------|----------|----------|

Relative score of "solution1" tag on 3 tests: 1.997
Average relative score: 0.66567
You have scored zero points on 1 seeds. Here are some of the seeds: [3]
```

#### tag &lt;tag_name1&gt; &lt;tag_name2&gt; ...
Compare the scores of the selected tags. Only the seeds that all the tags have in common will be compared. Examples:
```
>>> tag create solution1              # tag the solution with name "solution1"
>>> 1 10                              # run the seeds 1-10 and store them under "solution1" tag

( change source code of solution )
>>> tag create solution2              # tag the another solution with name "solution2"
>>> 5 15                              # run the seeds 5-15 and store them under "solution2" tag
>>> tag solution1 solution2           # compare the scores of seeds 5-10 (the ones they have in common)
|----------|-------------|-------------|---------|
|     Seed |   solution1 |   solution2 |    Best |
|----------|-------------|-------------|---------|
|        5 |   (+) 10.00 |        9.00 |   10.00 |
...
|       10 |      121.00 |  (+) 123.00 |  123.00 |
|----------|-------------|-------------|---------|
| Relative |     4.33199 |     4.79096 |       6 |
|  Average |     0.72199 |     0.79849 |    1.00 |
|    # (*) |           2 |           5 |       / |
|    # (+) |           1 |           1 |       / |
|----------|-------------|-------------|---------|

( change source code again )
>>> tag create solution3              # tag the another solution with name "solution3"
>>> 9 10                              # run the seeds 9-10 and store them under "solution3" tag
>>> tag solution1 solution2 solution3 # compare the scores of seeds 9-10
|----------|-------------|-------------|-------------|---------|
|     Seed |   solution1 |   solution2 |   solution3 |    Best |
|----------|-------------|-------------|-------------|---------|
|        9 |   (+) 10.00 |        9.00 |        2.00 |   10.00 |
|       10 |      121.00 |  (+) 123.00 |      100.00 |  123.00 |
|----------|-------------|-------------|-------------|---------|
| Relative |     1.66398 |     1.58193 |     1.30212 |       2 |
|  Average |     0.83199 |     0.79096 |     0.65106 |    1.00 |
|    # (*) |           0 |           0 |           0 |       / |
|    # (+) |           1 |           1 |           0 |       / |
|----------|-------------|-------------|-------------|---------|
```

#### tag create &lt;tag_name&gt;
Tag the current solution with name *tag_name*. Examples:
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
Delete the tag *tag_name*. Examples:
```
>>> tag delete solution1
Are you sure you want to delete tag "solution1"? [y/n]  y
Tag "solution1" was deleted.
```


Tips and tricks
---------------

- If your solution gets stuck, press ```q``` to easily terminate it. If you are running multiple tests, it terminates the whole execution (best scores of already run tests are still saved, though).
- If your solution crashes on some seed and you want to debug it, you can find input data of this seed in file specified by *testcase* field in *marathoner.cfg*.
- You can find the log of the last multitest run in the project directory, called *multiple_tests.log*.
- When you run multiple tests, standard error output from your solution is not displayed. But lines starting with ```!``` are displayed, still.
- Marathoner stores the source code of all the tagged solutions in ```<project_directory>/tags``` directory, so you can later return to them. You can use this as a simple version control system.
- If you internally measure running time of your solution, output to standard error a line in format: ```Run time = <run_time>```. Marathoner will use this time instead of the one it measures externally, which can be imprecise.
