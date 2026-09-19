"""
FuturSet Jobs Portal - Launcher Script
"""
import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f"  FuturSet Rojgar Portal - Government Job Intelligence")
    print(f"  Portal URL: http://{HOST}:{PORT}")
    print(f"  Gujarat Hub: http://{HOST}:{PORT}/gujarat")
    print(f"  API Docs: http://{HOST}:{PORT}/docs")
    print(f"=======================================================\n")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
