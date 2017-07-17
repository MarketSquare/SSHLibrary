*** Settings ***
Force Tags          pybot  linux
Resource            resources/common.robot
Test Teardown       Close All Connections

*** Variables ***
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY}               ${KEY DIR}${/}id_rsa
${KEY USERNAME}      testkey

*** Test Cases ***
Login Through Proxy Machine
    ${sock}  Proxy Through  ${HOST}  ${KEY USERNAME}  ${KEY}  ${HOST}
    Open Connection  ${HOST}  sock=${sock}
    Login  ${USERNAME}  ${PASSWORD}  sock=${sock}
    ${result}  Execute Command  pwd
    Should Be Equal  ${result}  /home/test

Switch Proxy Connection
    ${sock}  Proxy Through  ${HOST}  ${KEY USERNAME}  ${KEY}  ${HOST}
    ${conn1_id} =  Open Connection  ${HOST}  sock=${sock}  alias=one  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}  sock=${sock}
    Write  cd /tmp
    Read Until Prompt
    ${conn_id2} =  Open Connection  ${HOST}  alias=second  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}
    ${prev id} =  Switch Connection  ${conn1_id}
    Should Be Equal  ${prev id}  ${conn_id2}
    Write  pwd
    ${output} =  Read Until Prompt
    Should Contain  ${output}  /tmp
    ${prev id} =  Switch Connection  second
    Write  pwd
    ${result} =  Read Until Prompt
    Should Contain  ${result}  ~
