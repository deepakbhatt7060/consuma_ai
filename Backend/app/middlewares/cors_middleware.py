from fastapi.middleware.cors import CORSMiddleware

# Function to add CORS middleware to FastAPI app
def add_cors_middleware(app):
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["GET", "POST"],
		allow_headers=["*"]
	)
