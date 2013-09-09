
if [ "$(basename $PWD)" != "atest" ]; then
    OUTPUT_ROOT="atest/"
    COMMON_ARGS="-P src"
    JAR_ROOT="lib/"
else
    OUTPUT_ROOT=""
    COMMON_ARGS="-P ../src"
    JAR_ROOT="../lib/"
fi

OUTPUT_ROOT+="results"
JAR_ROOT+="trilead-ssh2-build213.jar"

if [ "$1" == "jython" ]; then
    shift
    OUTPUT_DIR="$OUTPUT_ROOT/jython"
    rm -rf $OUTPUT_DIR 2> /dev/null
    jybot $COMMON_ARGS -P $JAR_ROOT -d $OUTPUT_DIR -i jybot $*
elif [ "$1" == "python" ]; then
    shift
    OUTPUT_DIR="$OUTPUT_ROOT/python"
    rm -rf $OUTPUT_DIR 2> /dev/null
    pybot $COMMON_ARGS -d $OUTPUT_DIR -i pybot $*
else
    echo "Usage: atest/run_atests.sh (python|jython) <target>"
    exit 1
fi
