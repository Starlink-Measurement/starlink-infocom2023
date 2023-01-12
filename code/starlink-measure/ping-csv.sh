#!/bin/bash
#
# Do a ping and output results as CSV.
#
# dsimmons@squiz.co.uk
# 2011-12-23
#

if [ $# -lt 1 ]; then
	echo "Usage: $0 [--add-timestamp] <ping host>"
	exit 99
fi

opts=""
for opt in $*; do
	if [ "$opt" == "--add-timestamp" ]; then
		opts="$opts $opt"
		shift
	fi
done

trap echo 0

ping $* | while read line; do

	# Skip header
	[[ "$line" =~ ^PING ]] && continue

	# Skip non-positive responses
	[[ ! "$line" =~ "bytes from" ]] && continue

	# Extract address field
	addr=${line##*bytes from }
	addr=${addr%%:*}

	# Extract seq
	seq=${line##*icmp_seq=}
	seq=${seq%% *}

	# Extract time
	time=${line##*time=}
	time=${time%% *}

	echo -n "$addr,$seq,$time"

	# Calculate date (not totally accurate)
	if [[ "$opts" =~ "--add-timestamp" ]]; then
		timestamp=$(date +%s)
		echo -n ",$timestamp"
	fi

	echo

done
