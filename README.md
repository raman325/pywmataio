# WMATA

WMATA is an easy to use Python interface to the [Washington Metropolitan Area Transit Authority API](https://developer.wmata.com).

## Contents

- [WMATA](#wmata)
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
from wmata import MetroRail, Station

client = MetroRail(api_key)

trains = client.next_trains(Station["A01"])
```

### Design

WMATA breaks the WMATA API into two components: `MetroRail` and `MetroBus`.



#### `MetroRail`

Provides access to all MetroRail related endpoints.

##### Using `MetroRail`

```python
import wmata

client = wmata.MetroRail(api_key)

trains = client.next_trains(wmata.Station["A01"])
```

#### `MetroBus`

Provides access to all MetroBus related endpoints.



##### Using `MetroBus`

```python
from wmata import MetroBus

client = MetroBus(api_key)

routes = client.routes()
```



## Credits

Thanks to @emma-k-alexandra for [pywmata](https://github.com/emma-k-alexandra/pywmata) which I used as the base for this repo.



## License

WMATA is released under the MIT license. [See LICENSE](https://github.com/emma-k-alexandra/pywmata/blob/master/LICENSE) for details.
