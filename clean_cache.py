print("Step 1: remove .vercel/cache")
print("rm -r .vercel/cache")
print("Step 2: remove __pycache__ files")
print("find . __pycache__")
print("Check this works then -exec rm -r {} [LOOK THIS UP I FORGET]")
print("Step 3: run testing_tube.py to force the rebuild of the pickle files")
print("python -m tests.testing_tube")