OUTPUT_DIR="atest/results"
COMMON_FLAGS="-d $OUTPUT_DIR -P src -P lib/trilead-ssh2-build213.jar --critical regression"

if [ "$1" == "jython" ]; then
    RUNNER=jybot
elif [ "$1" == "python" ]; then
    RUNNER=pybot
else
    echo "Usage: atest/run_atests.sh (python|jython) suite"
    exit 1
fi

shift
$RUNNER $COMMON_FLAGS $*
