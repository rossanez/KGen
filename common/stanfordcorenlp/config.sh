#!/bin/bash

echo "Extracting the contents of the zip file..."
unzip stanford-corenlp-full-*.zip

echo "Creating the symbolic links..."
ln -s stanford-corenlp-full-*/stanford-corenlp-[0-9]-[0-9]-[0-9].jar stanford-corenlp.jar
ln -s stanford-corenlp-full-*/stanford-corenlp-[0-9]-[0-9]-[0-9]-models.jar stanford-corenlp-models.jar

echo "All set!"
