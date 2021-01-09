
# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning](https://calver.org/)

## Unreleased


### Added

* HDLC transport implementation
* TCP transport implementation
* DlMS client implementation
* Support for Get service including service specific block transfer
* Support for selective access via range descriptor
* Support for HLS authentication using HLS-GMAC.
* Support for GlobalCiphering
* Parsing of ProfileGeneric buffer

### Changed

* Changed project versioning scheme to Calendar versioning


### Deprecated


### Removed


### Fixed


### Security



## v0.0.2


### Changed

-   UDP messages are now based WrapperProtocolDataUnit to be able to reuse
    WrapperHeader for TCP messages.
-   Parsing of DLMS APDUs


### v0.0.1


Initial implementation.
