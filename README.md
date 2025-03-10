# ETrade Asset CLI

An ETrade CLI tool which is used to help calculate various investment metrics based on current account state.

## Requirements

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/etrade-asset-cli.git
    cd etrade-asset-cli
    ```

2. Install dependencies:

    ```sh
    poetry install
    ```

3. Create an `.env` file based on the `example.env` file and fill in the required values:

    ```sh
    cp example.env .env
    ```

## Usage

1. Run the script:

    ```sh
    poetry run python client.py
    ```

2. Follow the prompts to generate OAuth tokens if they are not already available.

## Environment Variables

The following environment variables need to be set in the  file:

- `ENV_TYPE`: Set to `prod` for production or `sandbox` for sandbox environment.
- `SANDBOX_CONSUMER_KEY`: Your sandbox consumer key.
- `SANDBOX_CONSUMER_SECRET`: Your sandbox consumer secret.
- `PROD_CONSUMER_KEY`: Your production consumer key.
- `PROD_CONSUMER_SECRET`: Your production consumer secret.
- `SANDBOX_BASE_URL`: The base URL for the sandbox environment.
- `PROD_BASE_URL`: The base URL for the production environment.
- `OAUTH_TOKEN`: The OAuth token (will be generated if not set).
- `OAUTH_TOKEN_SECRET`: The OAuth token secret (will be generated if not set).

## License

This project is licensed under the MIT License. See the LICENSE file for details.