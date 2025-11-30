"""Query API routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.cache.schema_cache import SchemaCache
from app.core.exceptions import (
    ConnectionException,
    LLMException,
    SchemaExtractionException,
    SecurityException,
    SQLExecutionException,
    SQLGenerationException,
)
from app.db.connection_manager import connection_manager
from app.db.schema_extractor import SchemaExtractor
from app.executor.query_runner import QueryRunner
from app.executor.result_handler import ResultHandler
from app.llm.sql_generator import SQLGenerator
from app.llm.sql_validator import SQLValidator
from app.models.query import QueryRequest, QueryResponse
from app.postprocessor.nl_response import NLResponseGenerator

router = APIRouter(prefix="/query")

schema_cache = SchemaCache()


@router.post(
    "/",
    response_model=QueryResponse,
    summary="Execute natural language query",
    description="Convert a natural language question to SQL and execute it against the database."
)
async def execute_query(request: QueryRequest) -> QueryResponse:
    """
    Execute a natural language query.
    
    This endpoint:
    1. Connects to the specified database
    2. Extracts the schema (cached when possible)
    3. Uses LLM to generate SQL from the natural language question
    4. Validates and executes the SQL
    5. Returns results with optional natural language explanation
    """
    adapter = None
    
    try:
        # Get database connection
        adapter = await connection_manager.get_connection(request.connection)
        
        # Get or extract schema
        schema = await _get_schema(request.connection, adapter)
        
        # Generate SQL from question (use user's API key if provided)
        sql_generator = SQLGenerator(schema, api_key=request.api_key)
        generated_sql = await sql_generator.generate_sql(
            question=request.question,
            max_rows=request.max_rows
        )
        
        # Validate SQL
        validator = SQLValidator()
        validation_result = validator.validate(generated_sql)
        
        if not validation_result.is_valid:
            return QueryResponse(
                success=False,
                question=request.question,
                generated_sql=generated_sql if request.include_sql else None,
                error=f"SQL validation failed: {validation_result.error}",
                timestamp=datetime.utcnow()
            )
        
        # Execute query
        query_runner = QueryRunner(adapter)
        result, execution_time = await query_runner.run(
            sql=validation_result.sql,
            max_rows=request.max_rows
        )
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            try:
                nl_generator = NLResponseGenerator(schema, api_key=request.api_key)
                explanation = await nl_generator.generate(
                    question=request.question,
                    sql=validation_result.sql,
                    result=result
                )
            except Exception:
                # Fallback to simple response
                explanation = NLResponseGenerator.generate_simple_response(result)
        
        return QueryResponse(
            success=True,
            question=request.question,
            generated_sql=validation_result.sql if request.include_sql else None,
            result=result,
            explanation=explanation,
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow()
        )

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
    except (SQLGenerationException, LLMException) as e:
        return QueryResponse(
            success=False,
            question=request.question,
            error=f"SQL generation failed: {e.message}",
            timestamp=datetime.utcnow()
        )
    except SecurityException as e:
        return QueryResponse(
            success=False,
            question=request.question,
            error=f"Security validation failed: {e.message}",
            timestamp=datetime.utcnow()
        )
    except SQLExecutionException as e:
        return QueryResponse(
            success=False,
            question=request.question,
            error=f"Query execution failed: {e.message}",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if adapter:
            await adapter.disconnect()


@router.post(
    "/sql",
    response_model=QueryResponse,
    summary="Execute raw SQL query",
    description="Execute a pre-written SQL query (for advanced users)."
)
async def execute_raw_sql(
    connection: dict,
    sql: str,
    max_rows: int = 100
) -> QueryResponse:
    """
    Execute a raw SQL query.
    
    This endpoint validates and executes a pre-written SQL query.
    Only SELECT queries are allowed for security.
    """
    from app.models.connection import ConnectionConfig
    
    adapter = None
    
    try:
        config = ConnectionConfig(**connection)
        adapter = await connection_manager.get_connection(config)
        
        # Validate SQL
        validator = SQLValidator()
        validation_result = validator.validate(sql)
        
        if not validation_result.is_valid:
            return QueryResponse(
                success=False,
                question="[Raw SQL Query]",
                generated_sql=sql,
                error=f"SQL validation failed: {validation_result.error}",
                timestamp=datetime.utcnow()
            )
        
        # Execute query
        query_runner = QueryRunner(adapter)
        result, execution_time = await query_runner.run(
            sql=validation_result.sql,
            max_rows=max_rows
        )
        
        return QueryResponse(
            success=True,
            question="[Raw SQL Query]",
            generated_sql=validation_result.sql,
            result=result,
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow()
        )
        
    except SecurityException as e:
        return QueryResponse(
            success=False,
            question="[Raw SQL Query]",
            generated_sql=sql,
            error=f"Security validation failed: {e.message}",
            timestamp=datetime.utcnow()
        )
    except SQLExecutionException as e:
        return QueryResponse(
            success=False,
            question="[Raw SQL Query]",
            generated_sql=sql,
            error=f"Query execution failed: {e.message}",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if adapter:
            await adapter.disconnect()


async def _get_schema(connection, adapter):
    """Get schema from cache or extract from database."""
    # Try cache first
    try:
        cached = await schema_cache.get(
            host=connection.host,
            port=connection.port,
            database=connection.database
        )
        if cached:
            return cached
    except Exception:
        pass
    
    # Extract schema
    extractor = SchemaExtractor(adapter)
    schema = await extractor.extract()
    
    # Cache for future requests
    try:
        await schema_cache.set(
            host=connection.host,
            port=connection.port,
            database=connection.database,
            schema=schema
        )
    except Exception:
        pass
    
    return schema
