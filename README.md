# target-lightspeed

`target-lightspeed` is a Singer target for Lightspeed.


## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
target is available by running:

```bash
target-lightspeed --about
```

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Config file

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

base_url: It can be either "https://api.webshopapp.com" or "https://api.shoplightspeed.com" depending on how your store was set.

language: The language available for your store or the language that the store was configured to use.

Sample config:
```$json
{
  "base_url": "https://api.webshopapp.com",
  "language": "nl",
  "api_key": "my_api_key",
  "api_secret": "my_api_secret"
}
```


### Source Authentication and Authorization

## Usage

You can easily run `target-lightspeed` by itself or in a pipeline using.

### Executing the Target Directly

```bash
target-lightspeed --version
target-lightspeed --help
# Test using the "Carbon Intensity" sample:
tap-carbon-intensity | target-lightspeed --config /path/to/target-lightspeed-config.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `target-lightspeed` CLI interface directly using `poetry run`:

```bash
poetry run target-lightspeed --help
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the Meltano Singer SDK to
develop your own Singer taps and targets.
