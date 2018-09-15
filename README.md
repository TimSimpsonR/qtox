
# Quick Tox

Quick Tox generates a bash script which re-runs the commands for each environment defined in your Tox file in parallel and without running much of Tox's complex setup, which can result in massive time savings.









As soon as the first environment command fails, the bash script bombs out, saving you from seeing a mountain of unrelated input. If you run tools like [Black]() and [MyPy]() before running more complex tasks such as tests you c
