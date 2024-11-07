### Initial Setup
1. Install the required dependencies listed in `requirements-dev.txt`:

    ```bash
    pip install -r requirements-dev.txt
    ```

2. Set up and enable the pre-commit hook by running:

    ```bash
    pre-commit install
    ```

   From now on, every time you run `git commit`, the scripts will execute automatically.

### Run Pre-commit Scripts Without Committing
If you'd like to manually run all pre-commit checks without making a commit, use:

```bash
pre-commit run --all-files
```

### You can bypass pre-commit hooks and proceed with the commit using:
```bash
git commit --no-verify
```
