## 0.3.0

### Features
- Added `OmegaConfig` support ([#73](https://github.com/neptune-ai/kedro-neptune/pull/73))

### Fixes
- Replaced `AbstractDataSet`, `TextDataSet` and `CSVDataSet` with `AbstractDataset`, `TextDataset` and `CSVDataSet` respectively ([#73](https://github.com/neptune-ai/kedro-neptune/pull/73))
- Replaced `kedro.extras.datasets` with `kedro_datasets` ([#73](https://github.com/neptune-ai/kedro-neptune/pull/73))

### Changes
- Added `kedro_datasets` to requirements, and bumped `kedro` to `>=0.18.5` ([#73](https://github.com/neptune-ai/kedro-neptune/pull/73))

## 0.2.0

### Fixes
- If `neptune` 'enabled' flag in the config is set to `false`, no neptune-related actions are taken ([#68](https://github.com/neptune-ai/kedro-neptune/pull/68))


##  0.1.5

### Fixes
- Fixed some of latest `neptune-client` warning messages ([#58](https://github.com/neptune-ai/kedro-neptune/pull/58))
- Fixed failing run on latest MacOS 12 ([#58](https://github.com/neptune-ai/kedro-neptune/pull/58))

### Changes
- Removed `neptune` and `neptune-client` from base requirements for backward compatibility ([#62](https://github.com/neptune-ai/kedro-neptune/pull/62))
- Simplified example project and removed unrelated files ([#58](https://github.com/neptune-ai/kedro-neptune/pull/58))
- Better life-time of the internally created Run in `NeptuneRunDataSet` ([#58](https://github.com/neptune-ai/kedro-neptune/pull/58))
- Updated the integration for compatibility with `neptune-client` `1.0.0`. ([#59](https://github.com/neptune-ai/kedro-neptune/pull/59))

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
