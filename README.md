# Pytest-PinPoint
[![PyPI version](https://img.shields.io/pypi/v/pytest-pinpoint.svg)](https://pypi.org/project/pytest-pinpoint/)

A pytest plugin which runs SBFL algorithms to detect faults.

First five algorithms are based on what Spencer Pearson, José Campos, René Just, Gordon Fraser, Rui Abreu, Michael D. Ernst, Deric Pang, Benjamin Keller discribed in [Evaluating and improving fault localization](https://homes.cs.washington.edu/~rjust/publ/fault_localization_effectiveness_icse_2017.pdf).

#### reference

Pearson, S., Campos, J., Just, R., Fraser, G., Abreu, R., Ernst, M. D., ... & Keller, B. (2017, May). Evaluating and improving fault localization. In *2017 IEEE/ACM 39th International Conference on Software Engineering (ICSE)* (pp. 609-620). IEEE.

#### required installation

`pip install git+https://github.com/nedbat/pytest-cov.git@nedbat/contexts`

`pip install coverage>=5.1`

#### run pytest-pinpoint

General usage, top three ranked results:

`python -m pytest --cov=. --cov-context --cov-branch --pinpoint`

Show all ranked results:

`python -m pytest --cov=. --cov-context --cov-branch --pinpoint --show_all`

Show bottom three ranked results:

`python -m pytest --cov=. --cov-context --cov-branch --pinpoint --show_last_three`
