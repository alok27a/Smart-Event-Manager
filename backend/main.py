import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS middleware
from api.v1 import endpoints
from core.database import close_mongo_connection, connect_to_mongo

# Create a FastAPI app instance
app = FastAPI(
    title="Family Event Assistant API",
    description="An intelligent assistant to parse, categorize, and manage family logistics with user authentication.",
    version="2.4.1"
)

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ React dev server origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add startup and shutdown event handlers
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Include the router from the endpoints module
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Family Event Assistant API. Go to /docs for documentation."}

# It's good practice to allow running the app directly for development
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
