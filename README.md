# Stock Portfolio Aggregator

A web application that aggregates stock positions from multiple brokerage accounts into a single view. Currently supports Charles Schwab and Merrill Lynch (placeholder implementations).

## Features

- Integration with multiple broker APIs
- Secure storage of API credentials in Redis
- Aggregated view of stock positions across all brokers
- Modern web interface built with Flask and Tailwind CSS
- Docker support for easy deployment
- CLI tools for token management
- Mock data support for development

## Prerequisites

- Python 3.9 or higher
- Redis (can be run via Docker or installed locally)
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd stock-aggregator
```

2. Install the package in development mode:

```bash
pip install -e .
```

## Running the Application

### Option 1: Running Without Docker (Development)

1. Start Redis (choose one method):

```bash
# Using Docker for Redis only
docker run -d -p 6379:6379 redis

# OR using local Redis installation
redis-server
```

2. Set environment variables:

```bash
# Set Flask application
export FLASK_APP=stock_aggregator.app.main:app
export FLASK_ENV=development
export REDIS_URL=redis://localhost:6379/0
```

3. Run the Flask development server:

```bash
flask run --port 5001
```

The application will be available at <http://localhost:5001>

### Option 2: Running with Docker Compose

1. Build and start all services:

```bash
docker-compose up --build
```

The application will be available at <http://localhost:5000>

## Configuration

1. Edit `config.yml`:

```yaml
brokers:
  schwab:
    enabled: true
    use_mock: true  # Set to true to use mock data instead of real API
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    refresh_token: "your_refresh_token"
```

## Development

### Using Mock Data

1. Set `use_mock: true` in `config.yml` for the broker you want to test:

```yaml
brokers:
  schwab:
    enabled: true
    use_mock: true  # This will use mock data instead of real API calls
```

2. Start the application as described above

### Troubleshooting

1. If you encounter dependency issues:

```bash
# Uninstall problematic packages
pip uninstall flask werkzeug -y

# Install specific versions
pip install flask==2.0.1 werkzeug==2.0.1

# Reinstall the package
pip install -e .
```

2. If Redis connection fails:

   1. Check if Redis is running:

   ```bash
   redis-cli ping
   ```

   2. Verify Redis URL in environment:

   ```bash
   echo $REDIS_URL
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 