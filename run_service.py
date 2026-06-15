import os
import sys
import threading

# Ensure the current directory is on the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.service.property_service import serve as serve_grpc

def start_grpc():
    """Run gRPC server on GRPC_PORT (default 50054) in a background thread."""
    serve_grpc()

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(title="Property Service", version="1.0.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "property_service"}

    @app.get("/")
    def root():
        return {"service": "property_service", "protocol": "gRPC", "grpc_port": os.getenv("GRPC_PORT", "50054")}

    # Start gRPC in background thread
    grpc_thread = threading.Thread(target=start_grpc, daemon=True)
    grpc_thread.start()

    # Start HTTP (FastAPI) on Render's PORT — this is what Render's scanner detects
    http_port = int(os.getenv("PORT", "8000"))
    print(f"HTTP health server starting on port {http_port}...")
    uvicorn.run(app, host="0.0.0.0", port=http_port)
