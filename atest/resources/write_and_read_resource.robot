*** Settings ***
Resource        shell.robot

*** Variables ***
${COUNTER NAME}                  counter.txt
${INTERACTIVE TEST SCRIPT NAME}  test_interactive.sh
${INTERACTIVE TEST SCRIPT}       ${LOCAL SCRIPTS}${/}${INTERACTIVE TEST SCRIPT NAME}
${REPEAT TEST SCRIPT NAME}       test_repeat.sh
${REPEAT TEST SCRIPT}            ${LOCAL SCRIPTS}${/}${REPEAT TEST SCRIPT NAME}


