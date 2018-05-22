# Introduction
Some python implementation of Atlassian Tools' API

&nbsp;

# Requirements
- python 3.4+

&nbsp;

# Installation
- Without specifying a branch (or use master):

```
pip install git+https://github.com/apilassian.git
```

- Bypassing a branch:

```
pip install git+https://github.com/apilassian.git@develop
```


&nbsp;

# Example

Returns a list with all groups within Bitbucket

code:

```
from apilassian import bitbucket
from apilassian.session import Session

session = Session(url="https://myrepo.com/stash", username="foo", password="bar")

print(bitbucket.Group(session).all())
```


