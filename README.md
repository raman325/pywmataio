# wmataio

`wmataio` is an easy to use Python interface to the [Washington Metropolitan Area Transit Authority API](https://developer.wmata.com).

## Contents

- [wmataio](#wmataio)
  - [Contents](#contents)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Getting Started](#getting-started)
    - [Design](#design)
      - [`MetroRail`](#metrorail)
        - [Using `MetroRail`](#using-metrorail)
      - [`MetroBus`](#metrobus)
        - [Using `MetroBus`](#using-metrobus)
  - [Credits](#credits)
  - [License](#license)

## Requirements

- Python 3.10

## Installation

```bash
pip install wmataio
```

## Usage

### Getting Started

```python
from wmataio import MetroRail, Station

client = MetroRail(api_key)
await client.load_data()
stations: dict[str, Station] = client.stations
lines: dict[str, Line] = client.lines
```

### Design

`wmataio` breaks the WMATA API into two components: `MetroRail` and `MetroBus`.

#### `MetroRail`

Provides access to all MetroRail related endpoints.

##### Using `MetroRail`

```python
import wmataio

client = wmataio.client(api_key)

trains = await client.rail.next_trains_at_station(client.rail.stations["A01"])
```

#### `MetroBus`

Provides access to all MetroBus related endpoints.

##### Using `MetroBus`

```python
import wmataio

client = wmataio.client(api_key)

routes = await client.bus.get_all_routes()
```

## Credits

Thanks to @emma-k-alexandra for [pywmata](https://github.com/emma-k-alexandra/pywmata) which I used as the base for this repo.

## License

`wmataio` is released under the MIT license. [See LICENSE](https://github.com/emma-k-alexandra/pywmata/blob/master/LICENSE) for details.
