set +x

if [ "$1" == "jython" ]; then
    shift
    PYTHONPATH="src/:$PYTHONPATH" jython $*
elif [ "$1" == "python" ]; then
    shift
    PYTHONPATH="src/:$PYTHONPATH" python $*
else
    echo "Usage: utest/run_utests.sh (python|jython) <target>"
    exit 1
fi
