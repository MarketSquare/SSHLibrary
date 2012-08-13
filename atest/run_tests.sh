OUTDIR=results
PYBOT=
JYBOT=
if [ $1 = "pybot" ] ; then
    PYBOT=true;
    shift
elif [ $1 = "jybot" ] ; then
    JYBOT=true;
    shift
else
    PYBOT=true
    JYBOT=true
fi

COMMON_FLAGS="-d $OUTDIR -l NONE -r NONE -P src -P lib/trilead-ssh2-build213.jar --critical regression"

if [ $PYBOT != "" ]; then
    pybot $COMMON_FLAGS -o pybot_output $* atest
fi
if [ $JYBOT != "" ]; then
    jybot $COMMON_FLAGS -o jybot_output $* atest
fi
rebot -d $OUTDIR $OUTDIR/*.xml
