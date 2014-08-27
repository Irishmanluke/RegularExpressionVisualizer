
byHand:
	./createFSMS -ll
byGen:
	./createFSMS -lr
viewHand:
	less RegEx2FSM_LL.py
viewGen:
	less RegEx2FSM_LR.py
clean:
	rm *.dot *.png parser.out parsetab.py
