-- Create human member table
CREATE TABLE IF NOT EXISTS human_members (
    member_id SERIAL PRIMARY KEY,
    member_uuid UUID UNIQUE NOT NULL,
    member_name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create human member profiles table
CREATE TABLE IF NOT EXISTS human_member_profiles (
    profile_id SERIAL PRIMARY KEY,
    profile_uuid UUID UNIQUE NOT NULL,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES human_members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (member_uuid) REFERENCES human_members(member_uuid) ON DELETE CASCADE
);

-- Create virtual member table
CREATE TABLE IF NOT EXISTS virtual_members (
    member_id SERIAL PRIMARY KEY,
    member_uuid UUID UNIQUE NOT NULL,
    member_name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create virtual member profiles table
CREATE TABLE IF NOT EXISTS virtual_member_profiles (
    profile_id SERIAL PRIMARY KEY,
    profile_uuid UUID UNIQUE NOT NULL,
    custom_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES virtual_members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (member_uuid) REFERENCES virtual_members(member_uuid) ON DELETE CASCADE
);
