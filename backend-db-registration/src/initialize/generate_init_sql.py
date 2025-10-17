#!/usr/bin/env python3
import uuid
from pathlib import Path

import yaml


def generate_sql(yaml_data, member_type):
    """Generate SQL from YAML data"""
    member = yaml_data["member"]
    profile = yaml_data["profile"]

    # Generate UUID for member
    member_uuid = str(uuid.uuid4())

    # INSERT into member table
    member_sql = f"""
    INSERT INTO {member_type}_members (member_uuid, member_name)
    VALUES ('{member_uuid}', '{member['name']}');
    """

    # INSERT into profile table
    profile_sql = f"""
    INSERT INTO {member_type}_member_profiles (profile_uuid, member_uuid, {member_type}_id, bio)
    SELECT
        '{uuid.uuid4()}',
        '{member_uuid}',
        member_id,
        '{profile['bio'].replace("'", "''")}'
    FROM {member_type}_members
    WHERE member_uuid = '{member_uuid}';
    """

    return member_sql + profile_sql


def main():
    # Path to profile directory
    profiles_dir = Path(__file__).parent.parent / "seed_data" / "profiles"

    # Output SQL file
    output_file = Path(__file__).parent.parent / "seed_data.sql"

    with open(output_file, "w", encoding="utf-8") as f:
        # Process human members
        human_dir = profiles_dir / "human"
        for yaml_file in human_dir.glob("*.yaml"):
            with open(yaml_file, encoding="utf-8") as yf:
                yaml_data = yaml.safe_load(yf)
                f.write(generate_sql(yaml_data, "human"))

        # Process virtual members
        virtual_dir = profiles_dir / "virtual"
        for yaml_file in virtual_dir.glob("*.yaml"):
            with open(yaml_file, encoding="utf-8") as yf:
                yaml_data = yaml.safe_load(yf)
                f.write(generate_sql(yaml_data, "virtual"))


if __name__ == "__main__":
    main()
