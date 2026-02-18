# Publishing to PyPI

## One-time Setup

1. **Create PyPI account**: https://pypi.org/account/register/

2. **Create API token**:
   - Go to https://pypi.org/manage/account/token/
   - Create token with scope: "Entire account"
   - Copy the token (starts with `pypi-`)

3. **Add token to GitHub**:
   - Go to https://github.com/orathore93-hue/tars-cli/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token
   - Click "Add secret"

## Publishing a Release

1. **Update version** in `pyproject.toml`

2. **Create a git tag**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Create GitHub release**:
   - Go to https://github.com/orathore93-hue/tars-cli/releases/new
   - Choose the tag you just created
   - Add release notes
   - Click "Publish release"

4. **Automatic deployment**: GitHub Actions will automatically build and publish to PyPI

## Manual Publishing (Alternative)

```bash
pip install build twine
python -m build
twine upload dist/*
```

Enter your PyPI username and token when prompted.
