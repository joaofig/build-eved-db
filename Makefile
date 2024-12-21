download-data:
	mkdir ./data
	git clone https://bitbucket.org/datarepo/eved_dataset.git ./eved
	cp ./eved/data/eVED.zip ./data
	rm -rf ./eved
