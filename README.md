# Parcellab Track and Trace API

A FastAPI-based backend service that provides shipment tracking information & weather conditions at the destination.

## Features

- Track shipments using tracking number and carrier
- View detailed shipment information including articles
- Get current weather conditions at the destination
- Cached weather data to minimize API calls
- OpenAPI documentation
- Docker-based development environment

## Prerequisites

- Docker + Docker Compose
- OpenWeatherMap API key (get one at https://openweathermap.org/api)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/kirmalyshev/parcellab_challenge
   cd parcellab_challenge
   ```

2. Copy a `.env` file, update with your OpenWeatherMap API key:
   ```bash
   cp .env.example .env
   ```
   set `OPENWEATHERMAP_API_KEY=your_api_key_here` in `.env`

3. Start the application + create dataset:
   ```bash
   make up-d
   make migrations-up
   make generate_shipments
   curl localhost:8000/api/v1/shipments/
```

The application will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/swagger
- PostgreSQL: localhost:15432
- Redis: localhost:16379

## Available Commands

- `make up` - Start the application and all services
- `make up-d` - Start the application and all services, in detached mode
- `make down` - Down all services, remove containers
- `make test` - Run tests
- `make lint` - Run linting (ruff + mypy)
- `make generate_shipments` - to create shipments from task's description

## API Endpoints
### Get Shipment with Weather
```
GET /api/v1/shipments/{tracking_number}?carrier={carrier}
```
Returns shipment details including weather information at the destination.

### Create Shipment
```
POST /api/v1/shipments/
```
Creates a new shipment with articles.

### List All Shipments
```
GET /api/v1/shipments/
```
Returns a list of all shipments.

## Development

The application uses:
- Python 3.12
- FastAPI for the web framework
- SQLAlchemy for database ORM
- Redis for caching
- Poetry for dependency management
- Docker for containerization


## Production Considerations

To deploy this application to production, you would need to:
1. Set up proper environment variables
2. Configure a production-grade database
3. Set up Redis cluster
4. Configure proper logging and monitoring
5. Set up CI/CD pipeline
6. Configure proper security measures

For handling 1000 requests per second, you would need to:
1. Scale the API service horizontally
2. Use database read replicas
3. Implement proper caching strategies
4. Use a load balancer
5. Monitor and optimize database queries
6. Implement rate limiting

## License

This project is licensed under the MIT License.
