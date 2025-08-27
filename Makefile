init:
	uv init .
	uv sync

download-data:
	mkdir -p ./data
	git clone https://bitbucket.org/datarepo/eved_dataset.git ./eved
	git clone https://github.com/gsoh/VED.git ./ved
	cp ./eved/data/eVED.zip ./data
	cp ./ved/Data/*.xlsx ./data
	rm -rf ./eved
	rm -rf ./ved

build-signals:
	uv run build.py --signals

build-nodes:
	uv run build.py --nodes

docker-run:
	podman run -dt --rm --name valhalla \
	-p 8002:8002 \
	-v ./valhalla/custom_files:/custom_files \
	-e serve_tiles=True \
	ghcr.io/nilsnolde/docker-valhalla/valhalla:3.5.1

pod-run:
	podman run -dt --rm --name valhalla \
	-p 8002:8002 \
	-v ./valhalla/custom_files:/custom_files \
	ghcr.io/nilsnolde/docker-valhalla/valhalla:3.5.1

clean:
	rm -rf .venv/

lint:
	uvx ruff check .

fmt:
	uvx ruff check .
	uvx ruff format --check .
	uvx ruff check --select I .

format:
	uvx ruff format .
	uvx ruff check . --fix
	uvx ruff check --select I . --fix
