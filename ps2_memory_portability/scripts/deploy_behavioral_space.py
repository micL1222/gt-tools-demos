"""Safely create/update the six-file Hugging Face Space deployment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download
from huggingface_hub.errors import RepositoryNotFoundError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPACE_DIR = PROJECT_ROOT / "behavioral_space"
MANIFEST = (
    "app.py",
    "core.py",
    "store.py",
    "ui_text.py",
    "requirements.txt",
    "README.md",
)
PROJECT_MARKER = "A behavioral demonstration of AI memory portability"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--slug",
        default="ps2-stay-or-switch-memory-portability",
        help="Space slug within the authenticated personal namespace",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api = HfApi()
    identity = api.whoami()
    namespace = identity["name"]
    repo_id = f"{namespace}/{args.slug}"

    existing = False
    try:
        info = api.repo_info(repo_id=repo_id, repo_type="space")
        existing = True
    except RepositoryNotFoundError:
        info = None

    if existing:
        readme_path = hf_hub_download(
            repo_id=repo_id, repo_type="space", filename="README.md"
        )
        readme = Path(readme_path).read_text(encoding="utf-8")
        if PROJECT_MARKER not in readme:
            raise RuntimeError(
                f"Refusing to overwrite existing Space {repo_id}: project marker absent."
            )
        unexpected = {
            sibling.rfilename
            for sibling in info.siblings
            if sibling.rfilename not in {*MANIFEST, ".gitattributes"}
        }
        if unexpected:
            raise RuntimeError(
                f"Refusing to modify {repo_id}: unexpected files {sorted(unexpected)}"
            )
    else:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            private=False,
            exist_ok=False,
        )

    operations = [
        CommitOperationAdd(
            path_in_repo=filename,
            path_or_fileobj=str(SPACE_DIR / filename),
        )
        for filename in MANIFEST
    ]
    commit = api.create_commit(
        repo_id=repo_id,
        repo_type="space",
        operations=operations,
        commit_message="Deploy Stay or Switch behavioral artifact",
    )
    print(
        json.dumps(
            {
                "authenticated": True,
                "namespace": namespace,
                "repo_id": repo_id,
                "space_url": f"https://huggingface.co/spaces/{repo_id}",
                "revision": commit.oid,
                "updated_existing_project_space": existing,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
