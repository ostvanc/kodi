tzlocal
=======

This Python module returns a `tzinfo` object with the local timezone information under Unix and Win-32.
It requires `pytz`, and returns `pytz` `tzinfo` objects.

This module attempts to fix a glaring hole in `pytz`, that there is no way to
get the local timezone information, unless you know the zoneinfo name, and
under several Linux distros that's hard or impossible to figure out.

Also, with Windows different timezone system using pytz isn't of much use
unless you separately configure the zoneinfo timezone name.

With `tzlocal` you only need to call `get_localzone()` and you will get a
`tzinfo` object with the local time zone info. On some Unices you will still
not get to know what the timezone name is, but you don't need that when you
have the tzinfo file. However, if the timezone name is readily available it
will be used.

Maintainer
----------

* Lennart Regebro, regebro@gmail.com

Contributors
------------

* Marc Van Olmen
* Benjamen Meyer
* Manuel Ebert
* Xiaokun Zhu
* Cameris
* Edward Betts
* McK KIM
* Cris Ewing
* Ayala Shachar
* Lev Maximov
* Jakub Wilk
* John Quarles
* Preston Landers

(Sorry if I forgot someone)

License
-------

* MIT https://opensource.org/licenses/MIT
