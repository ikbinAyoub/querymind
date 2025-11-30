"""Schema API routes."""

from fastapi import APIRouter, HTTPException, status

from app.cache.schema_cache import SchemaCache
from app.core.exceptions import ConnectionException, SchemaExtractionException
from app.db.connection_manager import connection_manager
from app.db.schema_extractor import SchemaExtractor
from app.models.connection import ConnectionConfig
from app.models.schema import SchemaInfo

router = APIRouter(prefix="/schema")

# Global schema cache instance
schema_cache = SchemaCache()


@router.post(
    "/extract",
    response_model=SchemaInfo,
    summary="Extract database schema",
    description="Extract schema information (tables, columns, keys) from the connected database."
)
async def extract_schema(
    connection: ConnectionConfig,
    include_row_counts: bool = False,
    use_cache: bool = True
) -> SchemaInfo:
    """
    Extract database schema.
    
    Connects to the database and extracts all table and column information.
    Results can be cached for faster subsequent requests.
    """
    # Try to get from cache first
    if use_cache:
        try:
            cached_schema = await schema_cache.get(
                host=connection.host,
                port=connection.port,
                database=connection.database
            )
            if cached_schema:
                return cached_schema
        except Exception:
            pass  # Cache miss, continue with extraction

    try:
        adapter = await connection_manager.get_connection(connection)
        
        try:
            extractor = SchemaExtractor(adapter)
            schema = await extractor.extract(include_row_counts=include_row_counts)
            
            # Cache the result
            if use_cache:
                try:
                    await schema_cache.set(
                        host=connection.host,
                        port=connection.port,
                        database=connection.database,
                        schema=schema
                    )
                except Exception:
                    pass  # Cache write failure is not critical
            
            return schema
        finally:
            await adapter.disconnect()

    except ConnectionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "details": e.details}
        )
    except SchemaExtractionException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "details": e.details}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=SchemaInfo,
    summary="Refresh cached schema",
    description="Force refresh of cached schema by re-extracting from database."
)
async def refresh_schema(
    connection: ConnectionConfig,
    include_row_counts: bool = False
) -> SchemaInfo:
    """
    Refresh cached schema.
    
    Invalidates the cached schema and extracts fresh data from the database.
    """
    # Invalidate cache first
    try:
        await schema_cache.invalidate(
            host=connection.host,
            port=connection.port,
            database=connection.database
        )
    except Exception:
        pass  # Continue even if invalidation fails

    # Extract with cache disabled to force fresh extraction
    return await extract_schema(
        connection=connection,
        include_row_counts=include_row_counts,
        use_cache=False
    )


@router.post(
    "/summary",
    summary="Get schema summary",
    description="Get a text summary of the database schema suitable for LLM prompts."
)
async def get_schema_summary(
    connection: ConnectionConfig,
    use_cache: bool = True
) -> dict:
    """
    Get schema summary as text.
    
    Returns a formatted text representation of the schema.
    """
    schema = await extract_schema(
        connection=connection,
        include_row_counts=False,
        use_cache=use_cache
    )
    
    return {
        "database": schema.database_name,
        "table_count": len(schema.tables),
        "summary": schema.get_schema_summary()
    }
