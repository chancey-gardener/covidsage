#!/usr/bin/bash

# tell 
#prctl(PR_SET_PDEATHSIG, SIGHUP);

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
nlu_server_pid=$!
echo "Rasa nlu server running (PID: $nlu_server_pid) on localhost:5005";

python3 intent_handling.py
kill $nlu_server_pid

