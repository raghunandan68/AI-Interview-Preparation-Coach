-- Run this updated script in the Supabase SQL Editor to create the custom tables

DROP TABLE IF EXISTS interview_history CASCADE;
DROP TABLE IF EXISTS pusers CASCADE;

-- 1. Create the custom 'pusers' table (Bypassing built-in auth completely)
CREATE TABLE IF NOT EXISTS pusers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Update the 'interview_history' table to map to the new pusers table
CREATE TABLE IF NOT EXISTS interview_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES pusers(id) ON DELETE CASCADE,
    role VARCHAR(255) NOT NULL,
    round_type VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    feedback_report TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Note: We removed the trigger, the RLS policies, and the auth.users dependencies completely!
-- This means NO MORE RATE LIMITS. Everything is fully controlled by your python code now.
