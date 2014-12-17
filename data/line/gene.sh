!#/bin/bash
FILES=raw/*
for f in $FILES
do
	echo "Processing $f file..."
    grep "connected with" $f | awk '{if($2 == "server:") {print $1, "\t", $4, "\t", $11, "\t", $13}}' > $f.map
    grep "bits/sec" $f | awk '{if($(NF-8) == "server:") {print $(NF-9),"\t", $(NF-6), "\t", $(NF-1), "\t", $(NF)}}' > $f.speed
    awk 'FNR==NR{a[$1, "\t", $2]=$3 FS $4;next}{ print $0, a[$1, "\t", $2]}' $f.map $f.speed > $f.data
done

mv raw/*.map map/
mv raw/*.speed speed/
mv raw/*.data data/

bash rename.sh

