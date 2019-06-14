SpaceAPI directory
==================

The Space API directory is a list of hackerspaces that have the Space API
implemented.

If your hackerspace is missing in the list, fork the repository,
add your space and create a pull request in Github.

Find more information about the SpaceAPI on https://spaceapi.io.

The purpose of the directory is to provide a stable API with a list of all
hackerspaces for applications like [MyHackerspace] and similar.


remove_unresponsive.py
----------------------

* Python script that do GET requests on the enpoints and recreate
  `directory.json` only with endpoints answering with HTTP 200.
* Please run this script from withing the FIXME hackerspace network if possible,
  it might trigger DOS protection of some endpoints (See #49)

[MyHackerspace]: https://github.com/fixme-lausanne/MyHackerspace
