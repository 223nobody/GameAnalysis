"""
Main application entry point for the Question Service API.
FastAPI-based web server with AI question generation capabilities.
"""

import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config.config import load_config
from app.services.client import create_ai_service
from app.storage.database import init_database
from app.controllers.question import create_question_controller
from app.controllers.actions import create_actions_controller


# Global variables for dependency injection
ai_service = None
database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    global ai_service, database

    try:
        # Load configuration
        config = load_config()
        logging.info("配置加载成功")

        # Initialize services
        ai_service = create_ai_service(config)
        logging.info("AI服务初始化成功")

        # Initialize database
        import os
        db_path = os.path.abspath("question_service.db")
        print(f"DEBUG: 数据库路径: {db_path}")
        print(f"DEBUG: 当前工作目录: {os.getcwd()}")
        print(f"DEBUG: 数据库文件是否存在: {os.path.exists(db_path)}")

        database = await init_database("question_service.db")
        logging.info("数据库初始化成功")

        # Debug: Test database connection
        try:
            test_questions, test_total = await database.get_questions_paginated(page=1, page_size=3)
            print(f"DEBUG: 启动时数据库测试: 总数={test_total}, 问题数量={len(test_questions)}")
            logging.info(f"数据库测试: 总数={test_total}, 问题数量={len(test_questions)}")
        except Exception as e:
            print(f"DEBUG: 启动时数据库测试失败: {e}")
            logging.error(f"数据库测试失败: {e}")

        # Setup routes after services are initialized
        setup_api_routes(app)

        yield

    except Exception as e:
        logging.error(f"应用启动失败: {e}")
        raise
    finally:
        # Cleanup
        if database:
            await database.close()
        logging.info("应用关闭完成")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Question Service API",
        description="AI-powered programming question generation service",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Frontend origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}
    
    # API routes will be set up in lifespan after services are initialized
    
    # Setup static file serving
    setup_static_files(app)
    
    return app


def setup_api_routes(app: FastAPI):
    """
    Setup API routes with controllers after services are initialized.

    Args:
        app: FastAPI application instance
    """
    global ai_service, database

    # Question generation routes
    question_router = create_question_controller(ai_service, database)
    app.include_router(
        question_router,
        prefix="/api/questions",
        tags=["questions"]
    )

    # Statistics and management routes
    stats_router = create_actions_controller(database)
    app.include_router(
        stats_router,
        prefix="/api/stats",
        tags=["statistics"]
    )

    # Additional question management routes (CreateByHand, update, batch-delete)
    app.include_router(
        stats_router,
        prefix="/api/questions",
        tags=["questions"]
    )


def setup_static_files(app: FastAPI):
    """
    Setup static file serving for frontend assets.
    
    Args:
        app: FastAPI application instance
    """
    # Get project root directory
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent
    dist_path = root_dir / "client" / "dist"
    
    # Check if frontend dist directory exists
    if dist_path.exists():
        # Mount static assets
        app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")
        
        # Serve favicon
        @app.get("/favicon.ico")
        async def favicon():
            favicon_path = dist_path / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(favicon_path)
            raise HTTPException(status_code=404, detail="Favicon not found")
        
        # Serve frontend for all other routes (SPA fallback)
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            # Don't serve frontend for API routes
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="API endpoint not found")
            
            index_path = dist_path / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            raise HTTPException(status_code=404, detail="Frontend not found")
        
        logging.info(f"已加载静态资源: {dist_path}")
    else:
        logging.info(f"未找到静态资源目录: {dist_path}")


# Create the FastAPI application
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the application
    port = int(os.getenv("PORT", "8080"))
    logging.info(f"服务启动于端口 {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
