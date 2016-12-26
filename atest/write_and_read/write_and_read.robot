*** Settings ***
Resource        ../resources/write_and_read_resource.robot
Force Tags      pybot   jybot
Suite Setup     Login And Upload Test Scripts
Suite Teardown  Remove Test Files and Close Connections
Documentation   This test case is isolated to its own suite because if `Read` fails
...             because of timing issues, it will bleed to other test cases. Timing
...             issues are related to the speed of computer. If the test case is 
...             failing, increase delay for `Read`.

*** Test cases ***
Write And Read
    Write  ${REMOTE TEST ROOT}/${INTERACTIVE TEST SCRIPT NAME}
    Write  Mr. Ääkkönen
    ${output} =  Read    delay=1s
    Should Contain  ${output}  Hello Mr. Ääkkönen
