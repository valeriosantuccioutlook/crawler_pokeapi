## Crawler API

# Basic usage:

     1. Use the scraper POST service to persist all data
     2. Use the scraper PATCH service to add or update exisiting entities
     2. Use the GET service to retrieve entities

# Notes:

     If, for any reason, you have problems to reach the services in the command line type:
          
          `uvicorn crawler_api.main:crawler_api --host 0.0.0.0`
     
     and you should be able to reach the services.

     If you prefer, you can also run in debug mode just opening the project in container and run from launch.json
