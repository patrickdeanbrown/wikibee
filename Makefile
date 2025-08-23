.PHONY: install

# Install wiki-extractor with pipx and verify CLI is available
install:
	@command -v pipx >/dev/null 2>&1 || { echo "pipx is required: https://pipx.pypa.io/stable/installation/"; exit 1; }
	pipx install . --force
	wiki-extractor --help >/dev/null
	@echo "wiki-extractor installed and verified"
