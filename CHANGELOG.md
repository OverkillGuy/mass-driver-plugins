# Changelog for Mass Driver Plugins


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]


## v0.3.1 - 2023-04-03

## Added
- Update to mass-driver `0.11`


## v0.3.0 - 2023-03-29


### Added
- New "surgical" editing base-class `SurgicalFileEditor` (mass-driver plugin
  name `surgical-base`), for the most difficult file-parsing-based editing.
- New driver `surgical-ghactionparamswitch`, demonstrating surgical file editing
  subclassing for editing YAML files of Github Actions: replaces given key/value
  of parameters from selected github actions, leaving file otherwise intact.


## v0.2.0 - 2023-03-15


### Added
- New Patchdriver `yamlpatch` and `jsonpatch` using JSONPatch (RFC6902).
- New  jinja2-based `templater` Patchdriver
- Updated to mass-driver `0.9`

## v0.1.0 - 2022-12-27
### Added
- New python module `mass_driver_plugins`, exposed as shell command `mass-driver-plugins`
