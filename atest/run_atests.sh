COMMON_ARGS="-P src"
OUTPUT_ROOT="atest/results"

if [ "$1" == "jython" ]; then
    shift
    jybot $COMMON_ARGS -P lib/trilead-ssh2-build213.jar -d $OUTPUT_ROOT/jython -i jybot $*
elif [ "$1" == "python" ]; then
    shift
    pybot $COMMON_ARGS -d $OUTPUT_ROOT/python -i pybot $*
else
    echo "Usage: atest/run_atests.sh (python|jython) <target>"
    exit 1
fi
