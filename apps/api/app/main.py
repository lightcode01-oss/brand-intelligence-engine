from fastapi import FastAPI

app = FastAPI(
    title="Nomen API Gateway", 
    description="Engineering Foundation active",
    version="0.1.0-foundation"
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy", 
        "version": "0.1.0-foundation"
    }
```
