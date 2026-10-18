# Publish the viewer with GitHub Pages

The monorepo is on branch `main` in `ArohanD/georeferencing-demo`. Publishing uses the monorepo directly; no second checkout or generated-files branch is needed.

The workflow lives at [`.github/workflows/deploy-viewer.yml`](../../.github/workflows/deploy-viewer.yml), the location GitHub requires. It runs the app-owned build script and uploads **only `app/dist/`**. Shared data, research, tools, and local artifacts are excluded from the deployment.

## One-time GitHub setup

Do these steps before pushing the new workflow:

1. Open the repository's **Settings → Pages**. Under **Build and deployment → Source**, choose **GitHub Actions**. Do not create one of the suggested workflows; this repo already contains one.
2. Open **Settings → Environments → github-pages**. Under **Deployment branches and tags**, ensure the `main` branch is allowed. If selected branches are used, add a branch rule named `main`; keep any other rules you still need.
3. From the monorepo root, push the committed changes with `git push origin main`.
4. Open **Actions → Deploy viewer to GitHub Pages**. Wait for both `build` and `deploy` to succeed, then visit https://arohand.github.io/georeferencing-demo/ . The `/preview/` path remains supported.

If an earlier workflow run failed before the settings were ready, open that run and choose **Re-run all jobs** after correcting the settings. You do not need another commit.

The workflow deploys on pushes to `main` that change the app folder, workflow, or layout checker. To deploy manually, open **Actions → Deploy viewer to GitHub Pages → Run workflow**, select `main`, and run it. Other branches cannot run the deployment job.

The Pages folder selector in **Deploy from a branch** only supports the repository root or `/docs`; it will not list `app/`. Use **GitHub Actions** as the source. The workflow selects `app/dist/` for you.

## Build and inspect locally

From the repository root:

```bash
python3 app/scripts/package_demo.py
python3 tools/check_layout.py
python3 -m http.server 8001 --bind 127.0.0.1 --directory app/dist
```

Open http://localhost:8001/ . The `dist/` directory is ignored and can be regenerated. The build preserves the deployed URL structure and writes a checksummed `PUBLICATION-MANIFEST.json`. It does not push or publish.

After deployment, verify the public files against the same local build:

```bash
.venv313/bin/python app/scripts/verify_public.py
```

This check requires `requests` and internet access. Its output goes to `app/artifacts/publication-verification.json`, which is ignored. `legacy-publication-verification.json` in this directory is evidence from the old demo, not verification of the current deployment.

Older integration documents and JSON validation records may mention `publish/` paths. Those describe historical runs. Current builds and publishing use the paths on this page.

References: [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [publishing source configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
