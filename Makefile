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


podman-run:
	podman run -it --rm --name valhalla_gis-ops -p 8002:8002 \
	-v ./valhalla/custom_files:/custom_files \
	-e tile_urls=http://download.geofabrik.de/north-america/us/michigan-latest.osm.pbf \
	-e serve_tiles=True -e build_admins=True \
	docker.pkg.github.com/gis-ops/docker-valhalla/valhalla:3.3.0
