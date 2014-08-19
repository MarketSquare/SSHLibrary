#!/bin/bash

function silent_remove_dir {
    rm -rf $1 2> /dev/null
}

if [ "$(basename $PWD)" == "atest" ]; then
    OUTPUT_ROOT="results"
    COMMON_ARGS="-P ../src"
    JAR_PATH="../lib/"
else
    OUTPUT_ROOT="atest/results"
    COMMON_ARGS="-P src"
    JAR_PATH="lib/"
fi

if [ "$1" == "python" ]; then
    shift
    OUTPUT_DIR="$OUTPUT_ROOT/python"
    silent_remove_dir $OUTPUT_DIR
    pybot $COMMON_ARGS -d $OUTPUT_DIR --log NONE --report NONE -i pybot $*
elif [ "$1" == "jython" ]; then
    shift
    JAR_PATH+="trilead-ssh2-1.0.0-build217.jar"
    OUTPUT_DIR="$OUTPUT_ROOT/jython"
    silent_remove_dir $OUTPUT_DIR
    jybot $COMMON_ARGS -P $JAR_PATH --log NONE --report NONE -d $OUTPUT_DIR -i jybot $*
else
    echo "usage: $0 (python|jython) <test_suite_path>"
    echo ""
    echo "Examples:"
    echo "  Running all the tests with Pybot:"
    echo "    $0 python ."
    echo ""
    echo "  Pybot results are found in path 'atest/results/python/'"
    echo ""
    echo "  Running all the tests with Jybot:"
    echo "    $0 jython ."
    echo
    echo "  Jybot results are found in path 'atest/results/jython/'"
    echo ""
    exit 1
fi

python -m robotstatuschecker $OUTPUT_DIR/output.xml
rebot -d $OUTPUT_DIR $OUTPUT_DIR/output.xml
echo
echo "$? tests failed after status check."
