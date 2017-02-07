# check ~/.pypirc for credentials
# http://peterdowns.com/posts/first-time-with-pypi.html

increase-package-version.py

# register
# python3 setup.py register -r pypitest
# ............. OR ::::::::::::::::
# twine register dist/*
# twine register dist/angle-0.1.dev0.tar.gz 

# generate pip
#######################################################
rm dist/* # clear old
python3 setup.py sdist bdist_wheel --universal upload

# upload pip .egg
#######################################################
twine upload dist/*.whl
# python3 setup.py sdist upload -r pypi
