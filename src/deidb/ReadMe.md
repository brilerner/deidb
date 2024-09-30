# Overview

In the code folder, there is a manifest of the environments that have been created.

The first thing that needs to be performed is the creation of the key db.
It will automatically use the deidb environment that has most recently been created. If you would like to use a different environment, please specify that.
When you are inside a folder, and run deidb init.
`deidb init <filepath>`

This program is designed to be run from terminal by calling:
`deidb deid <filepath>`

# Future Improvements
- log the type of code that was used
- automatic prompting to exclude column names
- cap sensititivity
- synonym support


# LATER
- reidentify
- handle synonyms

- reapparearing issue

# POTENTIAL ISSUES 
 DEPRECATION: Legacy editable install of deidb==0.1 from file:///Users/brianlerner/Library/CloudStorage/OneDrive-DukeUniversity/projects/code/Duke/Dunn%20Code/deidentify (setup.py develop) is deprecated. pip 25.0 will enforce this behaviour change. A possible replacement is to add a pyproject.toml or enable --use-pep517, and use setuptools >= 64. If the resulting installation is not behaving as expected, try using --config-settings editable_mode=compat. Please consult the setuptools documentation for more information. Discussion can be found at https://github.com/pypa/pip/issues/11457