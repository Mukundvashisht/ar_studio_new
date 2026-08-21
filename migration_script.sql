-- Database Migration Script
-- Generated automatically

-- Alter existing tables

-- Fix column types in notification
ALTER TABLE notification ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in task
ALTER TABLE task ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE task ALTER COLUMN created_at TYPE DATETIME;
ALTER TABLE task ALTER COLUMN completed_at TYPE DATETIME;
ALTER TABLE task ALTER COLUMN due_date TYPE DATETIME;

-- Fix column types in featured_work
ALTER TABLE featured_work ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE featured_work ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in project_assignment
ALTER TABLE project_assignment ALTER COLUMN assigned_at TYPE DATETIME;

-- Add columns to user
ALTER TABLE user ADD COLUMN otp_created_at DATETIME;
ALTER TABLE user ADD COLUMN email_verified BOOLEAN;
ALTER TABLE user ADD COLUMN otp_secret VARCHAR(32);

-- Remove columns from user
ALTER TABLE user DROP COLUMN IF EXISTS otp_verified CASCADE;
ALTER TABLE user DROP COLUMN IF EXISTS otp_verified_at CASCADE;
ALTER TABLE user DROP COLUMN IF EXISTS two_factor_enabled CASCADE;

-- Fix column types in user
ALTER TABLE user ALTER COLUMN banned_at TYPE DATETIME;
ALTER TABLE user ALTER COLUMN created_at TYPE DATETIME;
ALTER TABLE user ALTER COLUMN last_login TYPE DATETIME;
ALTER TABLE user ALTER COLUMN restriction_until TYPE DATETIME;

-- Fix column types in client
ALTER TABLE client ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE client ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in chat_message
ALTER TABLE chat_message ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in activity
ALTER TABLE activity ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in project
ALTER TABLE project ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE project ALTER COLUMN created_at TYPE DATETIME;
ALTER TABLE project ALTER COLUMN start_date TYPE DATETIME;
ALTER TABLE project ALTER COLUMN end_date TYPE DATETIME;

-- Fix column types in comment
ALTER TABLE comment ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE comment ALTER COLUMN created_at TYPE DATETIME;

-- Fix column types in milestone
ALTER TABLE milestone ALTER COLUMN updated_at TYPE DATETIME;
ALTER TABLE milestone ALTER COLUMN created_at TYPE DATETIME;
ALTER TABLE milestone ALTER COLUMN completed_at TYPE DATETIME;
ALTER TABLE milestone ALTER COLUMN due_date TYPE DATETIME;