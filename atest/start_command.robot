*** Settings ***
Force Tags      pybot   jybot
Resource        resources/shell.robot
Suite Setup     Login And Upload Test Scripts
Suite Teardown  Remove Test Files And Close Connections

*** Test Cases ***
Start Command And Read Process Output With Defaults
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${stdout} =  Read Command Output
    Should Be Equal  ${stdout}  This is stdout

Start Command And Read Only Return Code
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${rc} =  Read Command Output    return_stdout=False   return_rc=yes
    Should Be Equal As Integers  ${rc}  0

Start Command And Execute Command
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${stdout} =  Execute Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME} Hello
    Should Be Equal  ${stdout}  Hello
    ${stdout} =  Read Command Output
    Should Be Equal  ${stdout}  This is stdout

Start Command And Read Process Output With Legacy Stdout
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${stdout} =  Read Command Output  STDOUT
    Should Be Equal  ${stdout}  This is stdout

Start Command And Read Process Output With Legacy Stderr
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${stderr} =  Read Command Output  stderr
    Should Be Equal  ${stderr}  This is stderr

Start Command And Read Process Output With Legacy Stdout And Stderr
    Start Command  ${REMOTE TEST ROOT}/${TEST SCRIPT NAME}
    ${stdout}  ${stderr} =  Read Command Output  both
    Should Be Equal  ${stdout}  This is stdout
    Should Be Equal  ${stderr}  This is stderr

Reading Command Output Without Command Started
    Run Keyword And Expect Error
    ...  No started commands to read output from.
    ...  Read Command Output
