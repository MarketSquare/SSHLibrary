*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections
Library        OperatingSystem

*** Test Cases ***
Open Connection
    Open Connection  ${HOST}

Close Connection
    [Setup]  Login As Valid User
    Close Connection
    Connection Should Be Closed

Close Connection Fails If No Connection
    Run Keyword And Expect Error  No open connection.  Close Connection

Switch Connection
    ${conn1_id} =  Open Connection  ${HOST}  alias=one  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}
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

Switch Connection To None
    [Setup]   Login As Valid User
    Switch Connection  ${NONE}
    Connection Should Be Closed

Enable Logging
    [Tags]   pybot
    [Setup]  Remove File  ${OUTPUTDIR}${/}sshlog.txt
    Enable SSH Logging  ${OUTPUTDIR}${/}sshlog.txt
    Login As Valid User
    File Should Not Be Empty  ${OUTPUTDIR}${/}sshlog.txt

Switch to closed connection pybot
    [Tags]   pybot
    Open Connection  ${HOST}  alias=SUT
    Login  ${USERNAME}  ${PASSWORD}
    Execute command   ls
    close connection
    switch connection   SUT
    Run keyword and expect error  Connection not open   Execute command   ls

Switch to closed connection jybot
    [Tags]   jybot
    Open Connection  ${HOST}  alias=SUT
    Login  ${USERNAME}  ${PASSWORD}
    Execute command   ls
    close connection
    switch connection   SUT
    Run keyword and expect error  IllegalStateException: Cannot open session*   Execute command   ls

Get pre-login banner without open connection
    [Tags]   pybot
    ${banner} =  Get Pre Login Banner  ${HOST}
    Should Be Equal  ${banner}  Testing pre-login banner\n

Get pre-login banner from current connection
    [Tags]   pybot
    Open Connection  ${HOST}  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}
    ${banner} =  Get Pre Login Banner
    Should Be Equal  ${banner}  Testing pre-login banner\n

*** Keywords ***
Connection Should Be Closed
    Run Keyword And Expect Error  No open connection.  Write  pwd
