# Public app publication

Public app: https://arohand.github.io/georeferencing-demo/
Source of truth: https://github.com/ncstate-chass-projects/tradingnetworks

The app assets in `app/public/`, `app/assets.json`, and the package_demo.py and
static_package.py packagers are copied from university main commit
`a6cbfb6f18a1f0e1c6b3bacf46f436bf85d46834` (2026-10-23).
The existing public Pages workflow uses `ubuntu-latest`, builds `app/dist/`,
validates it, and publishes only that static app package. Other historical files
in this repository are retained but are not published. GeoServer is unchanged.

For future updates, validate university main with
`python3 app/scripts/check_app.py`, sync its declared app assets and packager files
listed above into this repository, update the source commit recorded here, run
`python3 app/scripts/package_demo.py` and `python3 tools/check_layout.py`, and push.
Verify the deployment from the university checkout using
`python3 app/scripts/verify_public.py https://arohand.github.io/georeferencing-demo/`
and the browser tests.

This is a manual publication snapshot. University commits do not automatically
update this site. Do not copy private previews, credentials or research inputs.
