#!/usr/bin/bash


while getopts ":t" opt; do
	case ${opt} in
		t ) # update
		update_model=true
		;;
	esac
done

if [[ $update_model ]] ; then
	rm models/*;
	rasa train nlu --fixed-model-name nlu;
fi

if [[ -z models ]] ; then
	echo "No model found.. try running again with -t.";
	exit;
fi

rasa run --enable-api -m 'models/nlu.tar.gz' &
echo "Rasa nlu server running (PID: $!) on localhost:5005";

