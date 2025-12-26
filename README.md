# Poor Python Server

Minimal HTTP server written in pure Python without frameworks.

## Endpoints

- `/` — HTML page  
- `/json` — test JSON response  
- `/health` — health check  
- `/weather?city=Almaty` — current weather info  

## Supported cities

- Almaty  
- Astana  

## Run

```bash
python poor_server.py
```
## Notes
- Uses standard library only
- Demonstrates routing, query parsing and external API calls
