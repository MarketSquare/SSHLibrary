*** Settings ***
Force Tags          pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections

*** Variables ***
${PWD_COMMAND}      pwd
${HOME_DIR}         /home/test
${KEY DIR}          ${LOCAL TESTDATA}${/}keyfiles${/}proxy
${KEY USERNAME}     testkey
${KEY}              ${KEY DIR}${/}id_rsa

*** Test Cases ***
Login Through Proxy Machine
    Proxy Through  10.181.50.232  testkey  ${KEY}  10.255.11.71
    Login  test  test
    ${result}  Execute Command  ${PWD_COMMAND}
    Should Be Equal  ${result}  ${HOME_DIR}