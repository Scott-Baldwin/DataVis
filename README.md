# DataVis
Data visualization practice

# Setup
This project uses [UV](https://github.com/astral-sh/uv) as a package manager. Check out the UV [docs](https://docs.astral.sh/uv/) and [GitHub](https://github.com/astral-sh/uv) for more info.

Install uv from a terminal by running this command:
```
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If installed via the standalone installer above, uv can update itself to the latest version:
```
uv self update
```

Install project packages:
```
uv sync
```