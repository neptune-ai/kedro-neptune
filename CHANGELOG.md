## kedro-neptune 0.1.4

### Changes
- Moved `kedro_neptune` package to `src` directory ([#50](https://github.com/neptune-ai/kedro-neptune/pull/50))
- Poetry as a package builder ([#56](https://github.com/neptune-ai/kedro-neptune/pull/56))

## kedro-neptune 0.1.3

### Changes
- Changed integrations utils to be imported from non-internal package ([#45](https://github.com/neptune-ai/kedro-neptune/pull/45))

## kedro-neptune 0.1.2

### Fixes
- Fixed custom run id generation on catalog creation ([#42](https://github.com/neptune-ai/kedro-neptune/pull/42))
- Fixed parsing of `NEPTUNE_ENABLED` flag ([#43](https://github.com/neptune-ai/kedro-neptune/pull/43))

### Changed
- `planets` example migrated to Kedro 0.18 structure ([#41](https://github.com/neptune-ai/kedro-neptune/pull/41))

## kedro-neptune 0.1.1

### Features
- Support environment variables for enabled ([#35](https://github.com/neptune-ai/kedro-neptune/pull/35))

## kedro-neptune 0.1.0

### Changes
- Adapted to kedro 0.18 release ([#33](https://github.com/neptune-ai/kedro-neptune/pull/33))
- Dropped support for kedro 0.17 (incompatible with 0.18) and python 3.6 (unsupported by kedro 0.18)

## kedro-neptune 0.0.8

### Fixes
- Fixed accessing run after Model Registry release ([#31](https://github.com/neptune-ai/kedro-neptune/pull/31))

## kedro-neptune 0.0.7

### Fixes
- Fixed backward compatibility with latest neptune-client

## kedro-neptune 0.0.6

### Features
- Added `enabled` flag to neptune.yml to maintain that metadata logging into Neptune is enabled ([#20](https://github.com/neptune-ai/kedro-neptune/pull/20))

## kedro-neptune 0.0.5

### Fixes
- Disable traceback uploading in child nodes ([#18](https://github.com/neptune-ai/kedro-neptune/pull/18))

## kedro-neptune 0.0.4

_Initial development version_
