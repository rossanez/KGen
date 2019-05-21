#!/bin/bash

echo "Extracting the contents of the zip file..."
unzip stanford-corenlp-full-*.zip

echo "Resolving patterns..."

dir_pattern="stanford-corenlp-full-*"
directories=( $dir_pattern )
echo "Directory: ${directories[0]}"

cd ${directories[0]}

main_jar_pattern="stanford-corenlp-[0-9].[0-9].[0-9].jar"
main_jar=( $main_jar_pattern )
echo "Main jar: ${main_jar[0]}"

models_pattern="stanford-corenlp-[0-9].[0-9].[0-9]-models.jar"
models=( $models_pattern )
echo "Models jar: ${models[0]}"

slf4j_pattern="slf4j-*.jar"
slf4j=( $slf4j_pattern )
echo "slf4j jars: ${slf4j[0]}, ${slf4j[1]}"

ejml_pattern="ejml-*.jar"
ejml=( $ejml_pattern)
echo "ejml jar: ${ejml[0]}"

cd ..

echo "Creating the symbolic links..."
ln -s ${directories[0]}/${main_jar[0]} stanford-corenlp.jar
ln -s ${directories[0]}/${models[0]} stanford-corenlp-models.jar
ln -s ${directories[0]}/${slf4j[0]} slf4j-api.jar
ln -s ${directories[0]}/${slf4j[1]} slf4j-simple.jar
ln -s ${directories[0]}/${ejml[0]} ejml.jar


echo "All set!"
