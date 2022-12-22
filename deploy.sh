rm -rf dist build *.egg-info
python3 setup.py sdist bdist_wheel
python3 setup.py install
rm -rf dist build *.egg-info