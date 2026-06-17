# Changelog

This release includes bug fixes and reliability improvements.

### Fixed
- Fixed challenge instance startup and shtudown by updating the implementation to use the currently supported HTB API route.
- Fixed challenge downloads when HTB does not provide a file hash, preventing valid downloads from being incorrectly treated as failed.