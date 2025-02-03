# Changelog for Mass Driver Plugins


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
The project uses semantic versioning (see [semver](https://semver.org)).

## [Unreleased]

### Added

- Updated to mass-driver `0.20`


## v0.5.0 - 2023-11-21

### Added

- Updated to mass-driver `0.18`

### Changed

- Replace `poetry` driver with `poetry-surgical`
  - Old version relied on "poetry-core" pkg, which removed "save" feature.
  - Replaced with version using so-called "surgical" editing via tree-sitter.
  - Other "surgical" editor (github actions one) is now a bit outdated, to be revised.


### Fixed

- Fix a couple edge cases of `SurgicalFileEditor` base class:
  - Now returns `PATCH_DOES_NOT_APPLY` on no such file found
  - Now returns `ALREADY_PATCHED` on identical file contents before/after

## v0.4.2 - 2023-11-12

### Added

- Updated to mass-driver `0.17`

## v0.4.1 - 2023-07-13


### Added
- Updated to mass-driver `0.16`


## v0.4.0 - 2023-07-05


### Added
- `TemplatedFile` PatchDriver now uses `Repo.patch_data` as jinja context. Repo
  metadata from repo discovery is thus usable directly.
- Updated to mass-driver `0.15`


## v0.3.2 - 2023-06-10

### Added
- Updated to mass-driver `0.14`


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
