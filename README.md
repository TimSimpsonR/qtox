# qtox

`qtox` creates Bash scripts that simply run the same commands Tox would run but in parallel for each environment.

This can lead to a massive speed-up in your daily local workflow.

## Benchmarks

I cloned the [Falcon web API framework](https://github.com/falconry/falcon), ran `tox` once, and commented out the script `tools/clean.sh` (which error'd out when the unit tests for Python 27 and 36 were run in parallel).

Following that, here's the output of `time tox` took:

real    1m9.746s
user    1m18.527s
sys 0m4.732s

I then created a bash script using `qtox --envs pep8 py27 py36 docs  > retox.sh`. Here's the output of `time ./retox.sh`:

real    0m40.326s
user    1m28.318s
sys 0m3.717s

So `qtox`'s script ran in 57% the time.

## Why you shouldn't call Tox from your dev box

Tox is great for making sure tests run a truly isolated environment on a CI platform, but if you're just trying to run flake8 or the unit tests for the hundredth time today it can be overkill.

Tox appears to do a lot of house work before running even the simplest commands. Anecdotally, I've always noticed a huge speed improvement when I simply ran a command in the virtualenv tox set up (say, `.tox/py27/bin/pytest mypkg`) versus when I invoked Tox directly (`tox -e py27`).

The speed savings were significant enough that I ended up writing Bash scripts to run the Tox commands and used that instead of Tox, which always ended up being faster according to [time](https://en.wikipedia.org/wiki/Time_%28Unix%29). On the downside, these scripts obviously duplicated information already found in the `tox.ini` file and often became out of date.

The rise of truly amazing static analysis tools in Python such as [MyPy](http://mypy-lang.org/) exacerbate the problems I see running invoking Tox compared to manually crafting scripts. Tools like MyPy offer the most value when they're run continuously as development happens. However, because MyPy checks are often put in separate tox environment, it's easy for people focused on a different problem (say, fixing a unit test) to run only those environments for minutes or hours before they remember to check MyPy, and be left needing to fix a bunch of type errors after they're convinced they've already made their program work at runtime.

The best solution is to just run everything as often as possible. `qtox` enables this.

## How to use qtox

Imagine a tox file that:

* formats your code with [Black](https://github.com/ambv/black)
* checks it with [Flake8](http://flake8.pycqa.org/en/latest/)
* checks it with MyPy
* runs unit tests in Python 3.5 and 3.6

Note: tox needs to run one time before `qtox` can be used, in order for qtox to determine if command line tools are present in the virtualenv's or if they should be checked for in the Tox's `whitelist_externals` setting. `qtox` doesn't replace Tox, it just lets you augment it with the ability to re-run it's commands faster.

`qtox` can be used to create a bash script like so:

    ```
    qtox --envs black pep8 mypy py35 p36 > retox.sh
    chmod +x retox.sh
    ```

When this script will instantly launch five jobs in parallel and wait on the results in the order you specified (meaning you want the quicker jobs- such as black or flake8- to run first).

As it works it's way through the list, it shows the output of each job in real time. So in this example, blacks output would be seen as it happens, and when black finishes all of flake8's output that happened in the interim will be shown before it's current output is displayed, etc.

It does this by having every job redirect to a file. When it's time to consume the results of that job, `tail` is invoked in another job, which reads from the start of the file and follows it until the process writing to it dies.

If a job fails, all other subsequent jobs are simply killed without printing out their output. This keeps things simpler so you don't have to scroll back up to see what went wrong.

It's up to you to make sure the simpler jobs are put earlier in the list you give to `qtox`. If you instead put the longer running jobs first, you'll have to wait for them to finish before seeing feedback from quicker tools such as flake8.
