# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Security
- Installer upgrades now read known `.env` values as plain `KEY=value` data instead of sourcing the existing environment file, preventing shell commands embedded in a compromised or malformed upgrade configuration from executing as root.

### Added
- Installer deployments can now target an exact 40-character commit SHA as well as a reviewed branch, providing an immutable manual deployment path.

### Changed
- CI now validates Bash syntax for repository deployment and update scripts without executing privileged installation or update operations.
- Review workflow tests now use an isolated database fixture and Ruff-compliant import/formatting fixes, restoring the full CI pipeline to green.
- CI now pins GitHub Actions to immutable commit SHAs while retaining their documented major versions.

## [1.0.0] - 2026-08-23

### Added
- Initial documented 1.0.0 release baseline for the self-hosted Review Intelligence Platform.
- Safe manual and scheduled Docker Compose update path with fast-forward-only updates and rollback on deployment failure.

### Changed
- Automated CI validates tests, formatting, linting, Python compilation, Docker Compose configuration and the production container build.
