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
- Daily portfolio snapshots with historical tracking

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

3. Install additional dependencies:

```bash
pip install plaid-python
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

## Snapshot Scheduler

The application includes a background scheduler that automatically generates daily snapshots of your portfolio. These snapshots track:

- Total account value
- Cash positions
- Open positions and their performance
- Historical changes in your portfolio

### Configuration

Add the following to your `config.yml`:

```yaml
snapshot_schedule:
  hour: 16    # 4 PM
  minute: 0   # Run at 4:00 PM
```

### Running the Scheduler

The snapshot scheduler starts automatically with the application. To manually trigger a snapshot:

```python
from stock_aggregator.app.services.snapshot_service import SnapshotService

snapshot_service = SnapshotService()
snapshot_service.generate_snapshot()  # Generate snapshot immediately
```

### Managing Snapshots

The scheduler automatically cleans up old snapshots to prevent database bloat. By default, it keeps 30 days of history. To change this:

```python
snapshot_service.cleanup_old_snapshots(days_to_keep=60)  # Keep 60 days of history
```

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

3. If snapshot generation fails:

   1. Check the application logs for error messages
   2. Verify database connection settings in `config.yml`
   3. Ensure all required broker connections are properly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 