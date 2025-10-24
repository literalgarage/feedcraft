TESTDATA_URL := "https://big-files.davepeck.dev/feedcraft/testdata.tar.gz"
TESTDATA_ARCHIVE := "testdata.tar.gz"
TESTDATA_DIR := "testdata"

default: lint format_check type_check test

lint:
    uv run ruff check

format_check:
    uv run ruff format --check

type_check:
    uv run pyright

download_testdata:
    @if [ ! -d "{{TESTDATA_DIR}}" ]; then \
        echo "Downloading test data from {{TESTDATA_URL}}..."; \
        curl -L -o "{{TESTDATA_ARCHIVE}}" "{{TESTDATA_URL}}"; \
        tar -xzf "{{TESTDATA_ARCHIVE}}"; \
        rm "{{TESTDATA_ARCHIVE}}"; \
    fi

test: download_testdata
    uv run pytest

watch:
    # Watch for changes and run tests.
    uv run ptw feedcraft/

clean:
    @echo "Cleaning up test data..."
    rm -rf {{TESTDATA_DIR}} {{TESTDATA_ARCHIVE}}


  
