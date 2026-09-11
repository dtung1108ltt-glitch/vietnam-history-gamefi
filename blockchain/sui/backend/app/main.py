from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, blockchain, faction, reward
from app.blockchain.sui_adapter import SuiAdapter
from app.core.config import get_settings
from app.core.security import NonceStore


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.settings = settings
    app.state.adapter = SuiAdapter(settings)
    app.state.nonce_store = NonceStore(settings.nonce_ttl_seconds)
    for router in (auth.router, faction.router, reward.router, blockchain.router):
        app.include_router(router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
