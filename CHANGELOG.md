# Changelog

This release includes bug fixes.

### Added
- None

### Improvements
- None

### Fixed

- #49: Fixed `machine start --script` on WSL when no login session is available.
- #50: Fixed `htb-operator init` failing on Parrot OS under WSL2 when `libarchive` could not load. The CLI now loads `libarchive` only when extracting a challenge archive and shows Parrot-specific installation guidance if loading fails.
