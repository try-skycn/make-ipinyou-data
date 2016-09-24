BASE=.
ORIGINALFOLDER=$(BASE)/original
ORIGINALDATA=$(ORIGINALFOLDER)/README
DATANAME=ipinyou.contest.dataset
TMP=$(BASE)/.tmp
TRAIN=$(TMP)/train
TEST=$(TMP)/test
TMPDATA=$(TMP)/data
ALL=$(TMPDATA)/all

SCRIPT=./script

DATA=$(BASE)/data
CLK=$(TMP)/clk.all.txt
TRAINDATA=train
TESTDATA=test

RUBBISH=.script

all: init advertisers expand recycle

$(ORIGINALFOLDER)/$(DATANAME).zip:
	@echo please link $(ORIGINALFOLDER)/$(DATANAME).zip to the data file $(DATANAME).zip; exit 1

$(ORIGINALDATA): $(ORIGINALFOLDER)/$(DATANAME).zip
	unzip $(ORIGINALFOLDER)/$(DATANAME).zip -d $(ORIGINALFOLDER)
	mv $(ORIGINALFOLDER)/$(DATANAME)/* $(ORIGINALFOLDER)
	rm -rf $(ORIGINALFOLDER)/$(DATANAME)
	rm -f $(ORIGINALFOLDER)/$(DATANAME).zip

init: $(ORIGINALDATA)
	mkdir -p $(TMP)
	mkdir -p $(TRAIN)
	cp $(ORIGINALFOLDER)/training2nd/imp.*.bz2 $(TRAIN)
	cp $(ORIGINALFOLDER)/training2nd/clk.*.bz2 $(TRAIN)
	cp $(ORIGINALFOLDER)/training3rd/imp.*.bz2 $(TRAIN)
	cp $(ORIGINALFOLDER)/training3rd/clk.*.bz2 $(TRAIN)
	bzip2 -d $(TRAIN)/*
	mkdir -p $(TEST)
	cp $(ORIGINALFOLDER)/testing2nd/* $(TEST)
	cp $(ORIGINALFOLDER)/testing3rd/* $(TEST)
	bzip2 -d $(TEST)/*
	mkdir -p $(ALL)

$(CLK): $(TRAIN)
	cat $(TRAIN)/clk*.txt > $@

$(ALL)/$(TRAINDATA): $(SCRIPT)/schema.txt $(CLK)
	cat $(TRAIN)/imp*.txt | $(SCRIPT)/mkdata.py $+ > $@
	$(SCRIPT)/formalizeua.py $@

$(ALL)/$(TESTDATA): $(SCRIPT)/schema.txt
	cat $(TEST)/*.txt | $(SCRIPT)/mktest.py $+ > $@
	$(SCRIPT)/formalizeua.py $@

advertisers: $(ALL)/$(TRAINDATA) $(ALL)/$(TESTDATA)
	$(SCRIPT)/splitadvertisers.py $(TMPDATA) 25 $(ALL)/$(TRAINDATA) $(ALL)/$(TESTDATA)

expand:
	bash $(SCRIPT)/expand.sh

clean:
	rm -rf $(TMP)
	rm -rf $(ORIGINALFOLDER)

recycle: clean
	mkdir -p $(RUBBISH)
	mv Makefile $(RUBBISH)
	mv script $(RUBBISH)
	rm -rf $(RUBBISH)
	git config core.sparseCheckout true
	echo ipinyoulib/ >> .git/info/sparse-checkout
	echo "/*" >> .gitignore
	echo "!ipinyoulib/" >> .gitignore
