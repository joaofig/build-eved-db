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

build:
	uv run build.py --signals