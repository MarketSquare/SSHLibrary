OUTDIR=results

pybot -d $OUTDIR -l pybot_log -r pybot_report -o pybot_output $* atest 
jybot -d $OUTDIR -l jybot_log -r jybot_report -o jybot_output \
 -P lib/trilead-ssh2-build213.jar $* atest
