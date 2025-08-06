import streamlit as st
import urllib
import pyodbc
from langchain_community.utilities import SQLDatabase

# Global database instance
db = None

def get_available_drivers():
    """Get list of available ODBC drivers"""
    try:
        drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
        return drivers
    except Exception as e:
        print(f"Error getting ODBC drivers: {e}")
        st.error(f"Error getting ODBC drivers: {e}")
        return []

def create_connection_string():
    """Create connection string with available ODBC driver"""
    available_drivers = get_available_drivers()
    
    if not available_drivers:
        raise Exception("No SQL Server ODBC drivers found. Please install ODBC Driver for SQL Server.")
    
    # Try drivers in order of preference
    preferred_drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server", 
        "ODBC Driver 13 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server"
    ]
    
    driver_to_use = None
    for preferred in preferred_drivers:
        if preferred in available_drivers:
            driver_to_use = preferred
            break
    
    if not driver_to_use:
        driver_to_use = available_drivers[0]  # Use first available
    
    print(f"Using driver: {driver_to_use}")
    st.info(f"🔧 Using driver: {driver_to_use}")
    
    odbc_str = (
        f"DRIVER={{{driver_to_use}}};"
        "SERVER=sirius1.ms-strategies.com,4123;"
        "DATABASE=pricetrack;"
        "UID=user1080703;"
        "PWD=homard;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=15;"  # Reduced timeout
        "Encrypt=no;"
    )
    
    return odbc_str

@st.cache_resource(show_spinner=False)
def get_sql_database():
    try:
        st.info("🗃️ Creating SQLAlchemy database instance...")
        print("Creating SQLAlchemy database instance...")
        
        # Create connection string with available driver
        odbc_str = create_connection_string()
        quoted_conn = urllib.parse.quote_plus(odbc_str)
        
        # Create SQLAlchemy connection
        conn_uri = f"mssql+pyodbc:///?odbc_connect={quoted_conn}"
        db = SQLDatabase.from_uri(conn_uri)
        
        return db
        
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")

def test_database_connection():
    """Test database connection with just ODBC"""
    try:
        print("Testing ODBC connection...")
        st.info("🔍 Testing ODBC connection...")
        
        # Test ODBC connection only
        odbc_str = create_connection_string()
        test_conn = pyodbc.connect(odbc_str)
        
        # Quick test query with timeout
        cursor = test_conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        test_conn.close()
        
        print("ODBC connection test successful!")
        st.success("✅ ODBC connection test successful!")
        return True
        
    except Exception as e:
        print(f"Database connection test failed: {e}")
        st.error(f"❌ Database connection test failed: {e}")
        return False

def get_database():
    """Get database instance with simplified connection testing"""
    global db
    
    try:
        print("Getting database instance...")
        st.info("🔄 Getting database instance...")
        
        # Test ODBC connection first
        if not test_database_connection():
            raise Exception("Database connection test failed")
        
        # Get the database instance (this creates SQLAlchemy connection)
        print("Creating SQLAlchemy database instance...")
        db_instance = get_sql_database()
        print("Database instance created successfully!")
        st.success("✅ Database instance created successfully!")
        
        # Set the global db variable
        db = db_instance
        
        # Test with SQL Server compatible syntax
        try:
            print("Testing database schema...")
            st.info("🔍 Testing database schema...")
            # Use SQL Server TOP syntax instead of LIMIT
            test_result = db_instance.run("SELECT TOP 1 * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            print("Database schema test successful!")
            st.success("✅ Database schema test successful!")
        except Exception as schema_error:
            print(f"Database schema test failed: {schema_error}")
            st.warning(f"⚠️ Database schema test failed: {schema_error}")
            # Don't fail completely, just warn
            print("Warning: Database schema test failed, but connection is established")
            st.warning("⚠️ Schema test failed, but connection is established")
        
        return db_instance
    except Exception as e:
        st.error(f"❌ Failed to get database: {e}")
        raise Exception(f"Failed to get database: {e}")

def get_table_info():
    """Get table information using SQL Server compatible syntax"""
    global db
    if db is None:
        return "Database not connected"
    
    try:
        # Get table names using SQL Server system views
        tables_query = """
        SELECT TOP 10 TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        result = db.run(tables_query)
        return result
    except Exception as e:
        return f"Error getting table info: {e}"

def get_db():
    """Helper function to get the database instance"""
    global db
    if db is None:
        db = get_database()
    return db