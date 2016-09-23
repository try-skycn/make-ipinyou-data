advertisers="1458 2261 2997 3386 3476 2259 2821 3358 3427 all"

for advertiser in $advertisers; do
	echo $advertiser
	python script/expand.py -f ./.tmp/data/$advertiser -t data/$advertiser --config script/config.py
done

