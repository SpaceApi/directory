SpaceAPI directory
==================

The SpaceAPI directory is a list of spaces that have the SpaceAPI
implemented.

If your space is missing in the [list](./directory.json), [fork the repository](https://github.com/SpaceApi/directory),
add your space and create a pull request in GitHub.

Find more information about the SpaceAPI on [spaceapi.io](https://spaceapi.io).

Directory Country
==================
directory-country-manual.json centralizes the country data from spaces that use the SpaceAPI.
Country data is static compared to volatile data like the space open status.
It is very rare for a space to move country, thus it makes sense to have this information as manual data.

To update the directory-country-manual.json execute "python run.py" to re-generate directory-country.json.
"diff -u directory-country.json directory-country-manual.json" and update directory-country-manual.json manually.
Or check the history directory.json since last commit of directory-country-manual.json and update manually.

"python read.py" generates statistics from new SpaceAPI directory format, and outputs them to worldwide-overview.txt.
Using worldwide-overview.txt you can hunt down the IDs of HackerSpaces that need their data updated.