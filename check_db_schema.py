import sys
import os
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
    MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint, CreateTable
)
from app import app, db

def get_database_uri():
    """Get the database URI from Flask config"""
    return app.config['SQLALCHEMY_DATABASE_URI']

def get_inspector(engine):
    """Get SQLAlchemy inspector for database reflection"""
    return inspect(engine)

def get_metadata():
    """Get SQLAlchemy metadata from models"""
    return db.metadata

def compare_schemas():
    """Compare database schema with SQLAlchemy models"""
    # Create engine and reflect database
    engine = create_engine(get_database_uri())
    inspector = get_inspector(engine)
    
    # Get metadata from models
    metadata = get_metadata()
    
    # Reflect the database schema
    db_metadata = MetaData()
    db_metadata.reflect(engine)
    
    # Get table names from both sources
    model_tables = set(metadata.tables.keys())
    db_tables = set(inspector.get_table_names())
    
    # Find differences
    tables_only_in_models = model_tables - db_tables
    tables_only_in_db = db_tables - model_tables
    common_tables = model_tables & db_tables
    
    # Compare columns for common tables
    column_differences = {}
    for table_name in common_tables:
        model_columns = {c.name: c for c in metadata.tables[table_name].c}
        db_columns = {c['name']: c for c in inspector.get_columns(table_name)}
        
        # Find column differences
        columns_only_in_model = set(model_columns.keys()) - set(db_columns.keys())
        columns_only_in_db = set(db_columns.keys()) - set(model_columns.keys())
        
        # Check column types and constraints
        type_mismatches = []
        for col_name in set(model_columns.keys()) & set(db_columns.keys()):
            model_col = model_columns[col_name]
            db_col = db_columns[col_name]
            
            # Compare types
            model_type = str(model_col.type).lower()
            db_type = str(db_col['type']).lower()
            
            # Normalize types for comparison
            if 'varchar' in db_type and 'character varying' in model_type:
                continue
            if db_type != model_type:
                type_mismatches.append({
                    'column': col_name,
                    'model_type': model_type,
                    'db_type': db_type
                })
        
        if columns_only_in_model or columns_only_in_db or type_mismatches:
            column_differences[table_name] = {
                'added_columns': list(columns_only_in_model),
                'removed_columns': list(columns_only_in_db),
                'type_mismatches': type_mismatches
            }
    
    # Check foreign key constraints
    fk_differences = {}
    for table_name in common_tables:
        model_fks = set()
        if table_name in metadata.tables:
            for fk in metadata.tables[table_name].foreign_keys:
                model_fks.add((fk.column.table.name, fk.column.name, fk.parent.name))
        
        db_fks = set()
        for fk in inspector.get_foreign_keys(table_name):
            db_fks.add((fk['referred_table'], fk['referred_columns'][0], fk['constrained_columns'][0]))
        
        if model_fks != db_fks:
            fk_differences[table_name] = {
                'model_foreign_keys': list(model_fks),
                'db_foreign_keys': list(db_fks)
            }
    
    return {
        'tables_only_in_models': list(tables_only_in_models),
        'tables_only_in_db': list(tables_only_in_db),
        'column_differences': column_differences,
        'foreign_key_differences': fk_differences
    }

def generate_migration_script(differences):
    """Generate SQL migration script based on schema differences"""
    engine = create_engine(get_database_uri())
    inspector = get_inspector(engine)
    metadata = get_metadata()
    
    migration_script = ["-- Database Migration Script", "-- Generated automatically"]
    
    # Drop tables that exist in DB but not in models (if any)
    if differences['tables_only_in_db']:
        migration_script.append("\n-- Drop tables that don't exist in models")
        for table_name in differences['tables_only_in_db']:
            migration_script.append(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    
    # Create tables that exist in models but not in DB
    if differences['tables_only_in_models']:
        migration_script.append("\n-- Create new tables")
        for table_name in differences['tables_only_in_models']:
            if table_name in metadata.tables:
                migration_script.append(f"\n-- Create table {table_name}")
                migration_script.append(str(CreateTable(metadata.tables[table_name]).compile(engine)))
    
    # Handle column differences for existing tables
    if differences['column_differences']:
        migration_script.append("\n-- Alter existing tables")
        for table_name, diffs in differences['column_differences'].items():
            if diffs['added_columns']:
                migration_script.append(f"\n-- Add columns to {table_name}")
                for col_name in diffs['added_columns']:
                    col = metadata.tables[table_name].c[col_name]
                    migration_script.append(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col.type};")
            
            if diffs['removed_columns']:
                migration_script.append(f"\n-- Remove columns from {table_name}")
                for col_name in diffs['removed_columns']:
                    migration_script.append(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {col_name} CASCADE;")
            
            if diffs['type_mismatches']:
                migration_script.append(f"\n-- Fix column types in {table_name}")
                for mismatch in diffs['type_mismatches']:
                    col = metadata.tables[table_name].c[mismatch['column']]
                    migration_script.append(f"ALTER TABLE {table_name} ALTER COLUMN {col.name} TYPE {str(col.type)};")
    
    # Handle foreign key differences
    if differences['foreign_key_differences']:
        migration_script.append("\n-- Update foreign key constraints")
        for table_name, diffs in differences['foreign_key_differences'].items():
            # Drop existing foreign keys that don't match the model
            for fk in diffs['db_foreign_keys']:
                migration_script.append(f"""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_schema = 'public' 
        AND table_name = '{table_name}' 
        AND constraint_name = '{table_name}_{fk[2]}_fkey'
    ) THEN
        ALTER TABLE {table_name} DROP CONSTRAINT {table_name}_{fk[2]}_fkey;
    END IF;
END $$;
""")
            
            # Add new foreign keys from the model
            for fk in diffs['model_foreign_keys']:
                migration_script.append(f"""
ALTER TABLE {table_name} 
ADD CONSTRAINT {table_name}_{fk[2]}_fkey 
FOREIGN KEY ({fk[2]}) 
REFERENCES {fk[0]}({fk[1]}) 
ON DELETE CASCADE;
""")
    
    return "\n".join(migration_script)

if __name__ == "__main__":
    with app.app_context():
        print("Comparing database schema with SQLAlchemy models...")
        differences = compare_schemas()
        
        print("\n=== Schema Differences ===")
        print(f"Tables only in models: {differences['tables_only_in_models']}")
        print(f"Tables only in database: {differences['tables_only_in_db']}")
        
        if differences['column_differences']:
            print("\nColumn differences:")
            for table, diffs in differences['column_differences'].items():
                print(f"\nTable: {table}")
                if diffs['added_columns']:
                    print(f"  Added columns: {', '.join(diffs['added_columns'])}")
                if diffs['removed_columns']:
                    print(f"  Removed columns: {', '.join(diffs['removed_columns'])}")
                if diffs['type_mismatches']:
                    print("  Type mismatches:")
                    for m in diffs['type_mismatches']:
                        print(f"    {m['column']}: model={m['model_type']}, db={m['db_type']}")
        
        if differences['foreign_key_differences']:
            print("\nForeign key differences:")
            for table, diffs in differences['foreign_key_differences'].items():
                print(f"\nTable: {table}")
                print(f"  Model FKs: {diffs['model_foreign_keys']}")
                print(f"  DB FKs: {diffs['db_foreign_keys']}")
        
        # Generate and save migration script
        migration_script = generate_migration_script(differences)
        with open('migration_script.sql', 'w') as f:
            f.write(migration_script)
        
        print("\nMigration script has been generated as 'migration_script.sql'")
        print("Review the script and apply it to your database using a tool like psql or pgAdmin.")
