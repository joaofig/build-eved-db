init:
	uv init .
	uv sync


download-data:
	mkdir ./data
	git clone https://bitbucket.org/datarepo/eved_dataset.git ./eved
	cp ./eved/data/eVED.zip ./data
	rm -rf ./eved

build:
	uv run build.py