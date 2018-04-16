# check ~/.pypirc for credentials
# http://peterdowns.com/posts/first-time-with-pypi.html

increase-package-version.py

# register
# python3 setup.py register -r pypitest

# generate pip
#######################################################
rm build/
rm dist/* # clear old
# python3 setup.py sdist bdist_wheel --universal 
# python3 setup.py sdist upload -r pypi
python3 setup.py sdist bdist_wheel --universal upload -r pypi

# twine register dist/*
# twine register dist/angle-0.1.dev0.tar.gz 


# upload pip .egg
#######################################################
twine upload dist/*.whl
