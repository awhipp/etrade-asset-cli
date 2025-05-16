# ETrade Asset CLI

An ETrade CLI tool which is used to help calculate various investment metrics based on current account state. This is largely a personal project to get metrics of interest to me, but feel free to use it as you see fit.

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
    poetry run python app.py --spy-strat
    poetry run python app.py --strategy-ui
    ```

2. Follow the prompts to generate OAuth tokens if they are not already available.

## Features

### SPY Strategy (`--spy-strat`)

The SPY strategy is a feature that analyzes SPY options to provide detailed information about:

1. **Call Option**: Includes details such as symbol, strike price, last price, bid, ask, volume, open interest, and Greeks (delta, gamma, theta, vega, and implied volatility).
2. **Put Option**: Includes the same details as the call option.
3. **Straddle Option**: Combines the call and put options at the same strike price and provides:
   - **Symbol**: The combined symbol for the straddle.
   - **Strike Price**: The strike price of the options.
   - **Last Price**: The combined last price of the call and put options.
   - **Bid**: The combined bid price of the call and put options.
   - **Ask**: The combined ask price of the call and put options.
   - **Break Even Lower**: The lower price boundary at which the straddle becomes profitable.
   - **Break Even Upper**: The upper price boundary at which the straddle becomes profitable.
   - **Break Even Distance**: The total cost of the straddle, representing how far the price needs to move in either direction to break even.

### Example Output

When running the SPY strategy with the command:

```sh
poetry run python app.py --spy-strat
```

You will see output similar to the following:

```plaintext
===== SPY STRATEGY RESULTS =====
Current SPY Price: $590.0
Expiry Date: 2025-05-16
Days to Expiry: 1

CALL OPTION:
Symbol: SPY May 16 '25 $590 Call
Strike Price: $590.0
Last Price: $2.37
Bid: $2.35
Ask: $2.37
Volume: 167491
Open Interest: 31700

Greeks:
  Delta: 0.52252
  Gamma: 0.08018
  Theta: -1.84601
  Vega: 0.11266
  IV: 0.17494

PUT OPTION:
Symbol: SPY May 16 '25 $590 Put
Strike Price: $590.0
Last Price: $1.89
Bid: $1.89
Ask: $1.91
Volume: 107174
Open Interest: 3971

Greeks:
  Delta: -0.47737
  Gamma: 0.08372
  Theta: -1.76913
  Vega: 0.11263
  IV: 0.16793

STRADDLE OPTION:
Symbol: SPY 590.0 Straddle
Strike Price: $590.0
Last Price: $4.26
Bid: $4.24
Ask: $4.28
Break Even Lower: $585.74
Break Even Upper: $594.26
Break Even Distance: $4.26
================================
```

This feature is particularly useful for traders analyzing straddle opportunities and assessing break-even points for SPY options.

### SPY Strategy Dashboard UI (`--strategy-ui`)

For a more interactive experience, you can use the SPY Strategy Dashboard UI which provides real-time updates on SPY option data:

```sh
poetry run python app.py --strategy-ui
```

This launches a web interface with the following features:

- **Real-time Updates**: Automatically refreshes data every 10 seconds
- **Side-by-side Comparison**: Call options displayed on the left, put options on the right
- **Straddle Analysis**: Complete straddle details with visual break-even points
- **Responsive Design**: Works well on desktop and mobile devices

The web interface provides a more convenient way to monitor option prices and straddle opportunities in real time. When you run the command, a browser window will automatically open to display the dashboard.

#### Screenshot

![SPY Strategy Dashboard](https://example.com/spy-dashboard-screenshot.png)

#### Technical Details

The dashboard is powered by:

- Flask web server running locally
- Automatic data polling via JavaScript
- Clean, modern UI with responsive design
- Visual indicators for break-even points

This feature is especially useful for traders who want to monitor SPY options continuously throughout the trading day without repeatedly running commands in the terminal.

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