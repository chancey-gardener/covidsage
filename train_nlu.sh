#!/bin/bash


rasa train nlu --fixed-model-name nlu;
cd models;

if [[ -d "nlu" ]] 
then
	rm -r nlu;
fi

tar -xvf nlu.tar.gz;

cd ..;
