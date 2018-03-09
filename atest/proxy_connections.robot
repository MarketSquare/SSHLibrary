*** Settings ***
Force Tags          pybot  linux
Resource            resources/common.robot
Resource            resources/sftp.robot
Test Teardown       Close All Connections

*** Variables ***
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY}               ${KEY DIR}${/}id_rsa
${KEY USERNAME}      testkey

*** Test Cases ***
Login Through Proxy Machine
    Login Through Proxy
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

SFTP Copy Through Proxy
    Login Through Proxy
    SSH.File Should Not Exist  ${REMOTE TEST ROOT}/${FILE WITH NON-ASCII NAME}
    Put File  ${FILE WITH NON-ASCII}  ${REMOTE TEST ROOT}/
    SSH.File Should Exist  ${REMOTE TEST ROOT}/${FILE WITH NON-ASCII NAME}
    [Teardown]  Execute Command  rm -rf ${REMOTE TEST ROOT}

*** Keywords ***
Login Through Proxy
    ${sock}  Proxy Through  ${HOST}  ${KEY USERNAME}  ${KEY}  ${HOST}
    Open Connection  ${HOST}  sock=${sock}
    Login  ${USERNAME}  ${PASSWORD}  sock=${sock}