OUTDIR=results
COMMON_FLAGS="-d $OUTDIR -P src -P lib/trilead-ssh2-build213.jar --critical regression"

pybot $COMMON_FLAGS -l pybot_log -r pybot_report -o pybot_output $* atest 
jybot $COMMON_FLAGS -l jybot_log -r jybot_report -o jybot_output $* atest
