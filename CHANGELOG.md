# Changelog

There are some bugfixes and changes.

### Added
- Extended `prolabs` command with dedicated subcommands:
  - `prolabs flags --id|--name`
  - `prolabs machines --id|--name`
  - `prolabs progress --id|--name`
  - `prolabs changelog --id|--name [--limit N]`
  - `prolabs reset-status --id|--name`

### Changed 
- 

### Fixed
- Improved ProLab progress/milestone parsing to handle API field variants (e.g. alternative milestone keys), preventing crashes like missing `is_milestone_reached`.
