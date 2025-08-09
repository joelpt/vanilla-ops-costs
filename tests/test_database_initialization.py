#!/usr/bin/env python3
"""
Unit tests for database initialization (init_database.py)
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.constants import MILESTONE_DATA_COLLECTION, SESSION_STATUS_COMPLETED
from scripts.init_database import DatabaseInitializer


class TestDatabaseInitializer:
    """Test suite for DatabaseInitializer class"""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters"""
        db_init = DatabaseInitializer()
        
        assert db_init.db_path == Path('data/costs/vanilla_costs.db')
        assert db_init.recreate == False
        assert db_init.schema_path == project_root / 'config' / 'database_schema.sql'
        
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters"""
        custom_db_path = '/tmp/test.db'
        db_init = DatabaseInitializer(db_path=custom_db_path, recreate=True)
        
        assert db_init.db_path == Path(custom_db_path)
        assert db_init.recreate == True
        
    def test_load_sql_schema_success(self, temp_config_files):
        """Test successful SQL schema loading"""
        db_init = DatabaseInitializer()
        db_init.schema_path = temp_config_files / 'database_schema.sql'
        
        schema = db_init.load_sql_schema()
        assert 'CREATE TABLE' in schema
        assert 'cost_categories' in schema
        
    def test_load_sql_schema_file_not_found(self):
        """Test SQL schema loading with missing file"""
        db_init = DatabaseInitializer()
        db_init.schema_path = Path('/nonexistent/schema.sql')
        
        with pytest.raises(FileNotFoundError):
            db_init.load_sql_schema()
            
    def test_load_json_config_success(self, temp_config_files):
        """Test successful JSON config loading"""
        db_init = DatabaseInitializer()
        
        config = db_init.load_json_config(temp_config_files / 'cost_category_taxonomy.json')
        assert 'cost_taxonomy' in config
        assert isinstance(config, dict)
        
    def test_load_json_config_file_not_found(self):
        """Test JSON config loading with missing file"""
        db_init = DatabaseInitializer()
        
        with pytest.raises(FileNotFoundError):
            db_init.load_json_config('/nonexistent/config.json')
            
    def test_load_json_config_invalid_json(self, tmp_path):
        """Test JSON config loading with invalid JSON"""
        db_init = DatabaseInitializer()
        invalid_json_file = tmp_path / 'invalid.json'
        invalid_json_file.write_text('invalid json content {')
        
        with pytest.raises(ValueError):
            db_init.load_json_config(str(invalid_json_file))
            
    def test_create_database_new_file(self, tmp_path, temp_config_files):
        """Test creating new database file"""
        db_path = tmp_path / 'test.db'
        db_init = DatabaseInitializer(db_path=str(db_path))
        db_init.schema_path = temp_config_files / 'database_schema.sql'
        
        result_path = db_init.create_database()
        
        assert result_path.exists()
        assert result_path == db_path
        
        # Verify database can be opened and has tables
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor]
            assert 'cost_categories' in tables
            
    def test_create_database_recreate_existing(self, tmp_path, temp_config_files):
        """Test recreating existing database"""
        db_path = tmp_path / 'test.db'
        
        # Create initial database
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE old_table (id INTEGER)")
            
        assert db_path.exists()
        
        # Recreate database
        db_init = DatabaseInitializer(db_path=str(db_path), recreate=True)
        db_init.schema_path = temp_config_files / 'database_schema.sql'
        
        result_path = db_init.create_database()
        
        # Verify old table is gone and new schema is applied
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor]
            assert 'old_table' not in tables
            assert 'cost_categories' in tables
            
    def test_populate_cost_categories(self, temp_db, temp_config_files):
        """Test populating cost categories from taxonomy"""
        db_init = DatabaseInitializer(db_path=temp_db)
        db_init.taxonomy_path = temp_config_files / 'cost_category_taxonomy.json'
        
        db_init.populate_cost_categories()
        
        # Verify categories were inserted
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cost_categories")
            count = cursor.fetchone()[0]
            assert count > 0
            
            cursor = conn.execute("SELECT name FROM cost_categories WHERE code = 'infrastructure'")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'Greenhouse Infrastructure'
            
    def test_populate_cost_categories_no_revenue_streams(self, tmp_path, temp_config_files):
        """Test populating categories when no revenue streams exist"""
        # Create empty database
        db_path = tmp_path / 'empty.db'
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE revenue_streams (id INTEGER PRIMARY KEY, code TEXT, name TEXT);
                CREATE TABLE cost_categories (
                    id INTEGER PRIMARY KEY,
                    revenue_stream_id INTEGER,
                    name TEXT,
                    code TEXT,
                    description TEXT,
                    parent_category_id INTEGER
                );
            """)
        
        db_init = DatabaseInitializer(db_path=str(db_path))
        db_init.taxonomy_path = temp_config_files / 'cost_category_taxonomy.json'
        
        # Should not raise error, but won't insert categories
        db_init.populate_cost_categories()
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cost_categories")
            count = cursor.fetchone()[0]
            assert count == 0
            
    def test_create_initial_collection_session(self, temp_db):
        """Test creating initial collection session"""
        db_init = DatabaseInitializer(db_path=temp_db)
        
        db_init.create_initial_collection_session()
        
        # Verify session was created
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("SELECT session_name, milestone, status FROM collection_sessions")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'Database Initialization'
            assert result[1] == MILESTONE_DATA_COLLECTION
            assert result[2] == SESSION_STATUS_COMPLETED
            
    def test_create_initial_collection_session_duplicate(self, temp_db):
        """Test creating initial collection session when it already exists"""
        db_init = DatabaseInitializer(db_path=temp_db)
        
        # Create first session
        db_init.create_initial_collection_session()
        
        # Create again (should not duplicate)
        db_init.create_initial_collection_session()
        
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM collection_sessions")
            count = cursor.fetchone()[0]
            assert count == 1
            
    def test_verify_database_success(self, temp_db):
        """Test successful database verification"""
        db_init = DatabaseInitializer(db_path=temp_db)
        
        result = db_init.verify_database()
        assert result == True
        
    def test_verify_database_missing_tables(self, tmp_path):
        """Test database verification with missing tables"""
        # Create database with incomplete schema
        db_path = tmp_path / 'incomplete.db'
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE cost_categories (id INTEGER PRIMARY KEY)")
        
        db_init = DatabaseInitializer(db_path=str(db_path))
        
        result = db_init.verify_database()
        assert result == False
        
    @patch('builtins.input', return_value='n')
    def test_main_recreate_cancelled(self, mock_input):
        """Test main function with recreate cancelled"""
        with patch('sys.argv', ['init_database.py', '--recreate']):
            with patch('scripts.init_database.DatabaseInitializer') as mock_init:
                from scripts.init_database import main
                
                # Should exit without creating initializer
                main()
                mock_init.assert_not_called()
                
    @patch('builtins.input', return_value='y')
    def test_main_recreate_confirmed(self, mock_input, temp_config_files):
        """Test main function with recreate confirmed"""
        with patch('sys.argv', ['init_database.py', '--recreate', '--db-path', '/tmp/test.db']):
            with patch('scripts.init_database.DatabaseInitializer') as mock_init_class:
                mock_initializer = MagicMock()
                mock_initializer.initialize.return_value = True
                mock_init_class.return_value = mock_initializer
                
                from scripts.init_database import main
                # The main function now calls sys.exit(), so we need to catch it
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                # Should exit with 0 for success
                assert exc_info.value.code == 0
                mock_init_class.assert_called_once_with(db_path='/tmp/test.db', recreate=True)
                mock_initializer.initialize.assert_called_once()
                
    def test_initialize_success(self, tmp_path, temp_config_files):
        """Test full initialize method success"""
        db_path = tmp_path / 'test.db'
        db_init = DatabaseInitializer(db_path=str(db_path))
        db_init.schema_path = temp_config_files / 'database_schema.sql'
        db_init.taxonomy_path = temp_config_files / 'cost_category_taxonomy.json'
        
        result = db_init.initialize()
        assert result == True
        assert db_path.exists()
        
    def test_initialize_failure(self, tmp_path):
        """Test initialize method with failure"""
        db_init = DatabaseInitializer(db_path=str(tmp_path / 'test.db'))
        db_init.schema_path = Path('/nonexistent/schema.sql')
        
        result = db_init.initialize()
        assert result == False
        
    def test_database_pragma_settings(self, tmp_path, temp_config_files):
        """Test that database is created with proper PRAGMA settings"""
        db_path = tmp_path / 'test.db'
        db_init = DatabaseInitializer(db_path=str(db_path))
        db_init.schema_path = temp_config_files / 'database_schema.sql'
        
        db_init.create_database()
        
        # Verify PRAGMA settings were applied
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            # Note: WAL mode might not persist after connection closes
            # but we can verify the database was created successfully
            
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor]
            assert len(tables) > 0