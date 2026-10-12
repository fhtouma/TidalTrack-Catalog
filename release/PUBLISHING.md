# Maintainer publication workflow

The owner authorized a public initial distribution and confirmed author order and licenses. No additional scientific approval gate is imposed on v0.1.0. Credentials are never included in this repository or archive.

## GitHub

Authenticate locally using GitHub CLI (`gh auth login --hostname github.com --git-protocol https --web`). Verify `gh api user --jq .login` returns `fhtouma`.

From a clean, committed checkout, if the proposed repository does not yet exist:

```bash
gh repo create fhtouma/TidalTrack-Catalog --public --source=. --remote=origin --push --description 'Catalogs from 480 controlled N-body tidal-evolution simulations'
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 dist/tidaltrack-catalog-v0.1.0.zip dist/SHA256SUMS --repo fhtouma/TidalTrack-Catalog --verify-tag --title 'TidalTrack Catalog v0.1.0' --notes-file release/v0.1.0.md
```

If the repository/tag/release already exists, inspect it and resume without overwriting existing content. Verify public visibility and download the archive from GitHub to compare its SHA256 to the local manifest.

## Zenodo

The dedicated Dataset record will contain the actual catalog ZIP and metadata; the GitHub integration alone should not be assumed to archive release attachments.

Create a token with `deposit:write` and `deposit:actions` via your Zenodo account applications page. Save it locally in `private/zenodo-token` with owner-only permissions, or set `ZENODO_ACCESS_TOKEN` in the process environment. Do not commit it or paste it into a public issue.

The upload tool additionally requires `requests` (`python3 -m pip install requests`). Its default invocation only verifies the local ZIP:

```bash
python3 scripts/publish_zenodo.py
python3 scripts/publish_zenodo.py --publish
```

The publishing command creates one deposition, saves its ID privately for resuming, streams files through the bucket API, compares remote MD5 checksums, verifies membership and publishes the record. It refuses conflicting existing files. On success, add the actual DOI and public record URL to the GitHub README and citation metadata in a follow-up commit. Do not replace an already published archive under the same version.

API reference: https://developers.zenodo.org/
GitHub release documentation: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
