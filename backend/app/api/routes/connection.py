"""Connection API routes."""

from fastapi import APIRouter, HTTPException, status

from app.core.exceptions import ConnectionException
from app.db.connection_manager import connection_manager
from app.models.connection import ConnectionConfig, ConnectionResponse, ConnectionTestRequest

router = APIRouter(prefix="/connection")


@router.post(
    "/test",
    response_model=ConnectionResponse,
    summary="Test database connection",
    description="Test if a database connection can be established with the provided credentials."
)
async def test_connection(request: ConnectionTestRequest) -> ConnectionResponse:
    """
    Test database connection.
    
    Validates the connection parameters and attempts to connect to the database.
    Returns success status and connection details.
    """
    try:
        success, message, connection_id = await connection_manager.test_connection(
            request.connection
        )

        if success:
            return ConnectionResponse(
                success=True,
                message=message,
                connection_id=connection_id,
                details={
                    "host": request.connection.host,
                    "port": request.connection.port,
                    "database": request.connection.database,
                    "db_type": request.connection.db_type.value
                }
            )
        else:
            return ConnectionResponse(
                success=False,
                message=message
            )

    except ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=ConnectionResponse,
    summary="Validate connection configuration",
    description="Validate connection parameters without actually connecting."
)
async def validate_connection(config: ConnectionConfig) -> ConnectionResponse:
    """
    Validate connection configuration.
    
    Performs basic validation of connection parameters.
    """
    # Basic validation is handled by Pydantic
    # Additional validation can be added here
    
    try:
        # Check if adapter exists for this database type
        connection_manager.get_adapter_class(config.db_type)
        
        return ConnectionResponse(
            success=True,
            message="Connection configuration is valid",
            details={
                "host": config.host,
                "port": config.port,
                "database": config.database,
                "db_type": config.db_type.value
            }
        )
    except ConnectionException as e:
        return ConnectionResponse(
            success=False,
            message=e.message
        )
