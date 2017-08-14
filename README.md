OpenSpaceDirectory
==================

The Space API directory is a list of hackerspaces that have the Space API
implemented.

If your hackerspace is missing in the list, fork the repository,
add your space and create a pull request in Github.

This is a fork version of the official [SpaceAPI](http://spaceapi.net),
aimed to ease the process of adding a space, provide a transparent and stable
API for the [MyHackerspace Android application](https://github.com/fixme-lausanne/MyHackerspace)


remove_unresponsive.py
----------------------

* Python script that do GET requests on the enpoints and recreate
  `directory.json` only with endpoints answering with HTTP 200.
* Please run this script from withing the FIXME hackerspace network if possible,
  it might trigger DOS protection of some endpoints (See #49)
