import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AsyncExclusivePeriods",
    version="1.0.0",
    author="Antas",
    author_email="",
    description='''
    Think about such scene, some object has different state or periods, well we call periods.Among these periods, there 
can't be any two that could be both the present period. The object could be in only one period. For example, a human can 
only be one period of baby, youth, adult, old man and dead.

So now not only can you get the exact period, but also await inside the period, await outside the period, await time when 
the object enters the period and await time when the object exits the period.

Remember to distribute different periods for one object.          
    ''',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/monk-after-90s/AsyncExclusivePeriods.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
