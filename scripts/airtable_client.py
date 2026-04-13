"""
Airtable client for GUJIYU video project tracking.
Tables: Projects, AI Avatars, AI Environments
"""
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

# Exact Airtable field names — must match your base exactly
PROJECT_FIELDS = {
    "ad_name": "Ad Name",
    "product_name": "Product Name",
    "image_prompt": "Image Prompt",
    "image_status": "Image Status",
    "image_generator": "Image Generator",
    "video_status": "Video Status",
    "video_generator": "Video Generator",
    "video_prompt": "Video Prompt",
    "generated_image_url": "Generated Image URL",
    "video_url": "Video URL",
}


class AirtableClient:
    def __init__(self, api_key: str, base_id: str):
        self.api = Api(api_key)
        self.base_id = base_id
        self.projects_table = os.getenv("AIRTABLE_PROJECTS_TABLE", "Projects")
        self.avatars_table = os.getenv("AIRTABLE_AVATARS_TABLE", "AI Avatars")
        self.environments_table = os.getenv("AIRTABLE_ENVIRONMENTS_TABLE", "AI Environments")

    def _table(self, table_name: str):
        return self.api.table(self.base_id, table_name)

    def create_project(self, fields: dict) -> dict:
        """Create a new project record. Returns the full record {id, fields, createdTime}."""
        return self._table(self.projects_table).create(fields)

    def update_project(self, record_id: str, fields: dict) -> dict:
        """Update fields on an existing project record."""
        return self._table(self.projects_table).update(record_id, fields)

    def get_project(self, record_id: str) -> dict:
        """Fetch a single project record by ID."""
        return self._table(self.projects_table).get(record_id)

    def list_projects(self, formula: str = None) -> list:
        """List all projects, optionally filtered by Airtable formula."""
        table = self._table(self.projects_table)
        if formula:
            return table.all(formula=formula)
        return table.all()

    def update_project_status(
        self,
        record_id: str,
        image_url: str = None,
        video_url: str = None,
        image_status: str = None,
        video_status: str = None,
        video_prompt: str = None,
        image_prompt: str = None,
    ) -> dict:
        """Convenience method for updating progress fields."""
        fields = {}
        if image_url:
            fields[PROJECT_FIELDS["generated_image_url"]] = image_url
        if video_url:
            fields[PROJECT_FIELDS["video_url"]] = video_url
        if image_status:
            fields[PROJECT_FIELDS["image_status"]] = image_status
        if video_status:
            fields[PROJECT_FIELDS["video_status"]] = video_status
        if video_prompt:
            fields[PROJECT_FIELDS["video_prompt"]] = video_prompt
        if image_prompt:
            fields[PROJECT_FIELDS["image_prompt"]] = image_prompt
        return self.update_project(record_id, fields)

    def get_avatar(self, name: str) -> dict | None:
        """Look up an avatar by name in the AI Avatars table."""
        records = self._table(self.avatars_table).all(
            formula=f"{{Name}} = '{name}'"
        )
        return records[0] if records else None

    def list_avatars(self) -> list:
        """List all avatars."""
        return self._table(self.avatars_table).all()

    def get_environment(self, name: str) -> dict | None:
        """Look up an environment by name in the AI Environments table."""
        records = self._table(self.environments_table).all(
            formula=f"{{Name}} = '{name}'"
        )
        return records[0] if records else None

    def list_environments(self) -> list:
        """List all available environments."""
        return self._table(self.environments_table).all()


def main():
    parser = argparse.ArgumentParser(description="Airtable client test")
    parser.add_argument("--test", action="store_true", help="Run connection test")
    parser.add_argument("--list-projects", action="store_true")
    parser.add_argument("--list-environments", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")

    if not api_key or not base_id:
        print("ERROR: AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set in .env")
        return

    client = AirtableClient(api_key, base_id)

    if args.test:
        print("Creating test project record...")
        record = client.create_project({
            PROJECT_FIELDS["ad_name"]: f"Test — {datetime.now():%Y-%m-%d %H:%M}",
            PROJECT_FIELDS["product_name"]: "Test Product",
            PROJECT_FIELDS["image_status"]: "pending",
            PROJECT_FIELDS["video_status"]: "pending",
        })
        print(f"Created record: {record['id']}")
        print(f"Fields: {record['fields']}")

    if args.list_projects:
        projects = client.list_projects()
        print(f"\nProjects ({len(projects)}):")
        for p in projects:
            print(f"  [{p['id']}] {p['fields'].get('Ad Name', 'Unnamed')}")

    if args.list_environments:
        envs = client.list_environments()
        print(f"\nEnvironments ({len(envs)}):")
        for e in envs:
            print(f"  {e['fields'].get('Name', 'Unnamed')}: {e['fields'].get('Vibe', '')}")


if __name__ == "__main__":
    main()
