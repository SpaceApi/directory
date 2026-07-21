SpaceAPI directory
==================

The SpaceAPI directory is a list of spaces that have the SpaceAPI
implemented.

If your space is missing in the [list](./directory.json), [fork the repository](https://github.com/SpaceApi/directory),
add your space and create a pull request in GitHub.

Adding or sorting entries
-------------------------

You can edit [directory.json](./directory.json) by hand, or use the helper
script [manage_directory.py](./manage_directory.py) (Python 3, standard library
only):

```bash
./manage_directory.py sort                       # sort directory.json in place
./manage_directory.py add                        # add an entry interactively
./manage_directory.py add -n "SedinaSpace" -u https://example.org/spaceapi.json
```

`add` rejects duplicate names and URLs and validates the endpoint with the
[SpaceAPI validator](https://validator.spaceapi.io/ui) (schema, HTTPS,
reachability, CORS and certificate) before writing. Its output matches the CI
`sort` job, so a sorted file stays byte-for-byte identical to
`jq -S directory.json`.

Find more information about the SpaceAPI on [spaceapi.io](https://spaceapi.io).

Some tips for correct implementation see information about [providing a endpoint](https://spaceapi.io/provide-an-endpoint/).

If you want to use the spaceapi directory, you can find it hosted under [https://directory.spaceapi.io/](https://directory.spaceapi.io/).
