# Sarah Pink — ORCID RSS

This project creates an RSS 2.0 feed from the public ORCID works endpoint for Sarah Pink (`0000-0003-0073-8382`). It checks daily via GitHub Actions.

## Publish your feed

1. Create a **public** GitHub repository named `sarah-pink-rss`.
2. Upload `generate.py` and the `.github/workflows/update.yml` file, preserving the directory structure. You can upload the files using Git or GitHub's web interface.
3. In the repository, open **Actions** and run **Update Sarah Pink RSS** manually once. The workflow creates `feed.xml` and commits it to the repository.
4. Under **Settings → Pages**, choose **Deploy from a branch**, `main`, `/ (root)` and save.
5. Subscribe to `https://YOUR-GITHUB-USERNAME.github.io/sarah-pink-rss/feed.xml` in your RSS reader. Replace the username with your own.

Note: If GitHub Actions cannot push, check repository Actions permissions under **Settings → Actions → General → Workflow permissions** and permit read/write access. GitHub's scheduled jobs can be delayed and may be disabled after extended inactivity.

## Run locally

`python generate.py`

The feed covers public ORCID works, not necessarily all published works. Publication dates represent publication dates where provided, not when a record was added to ORCID. The first subscription may show older items. The ORCID public API may be rate limited or require authorization in some contexts; if the workflow fails with an authorization error, ORCID API credentials and a read-public token will be needed.
