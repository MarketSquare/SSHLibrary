*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections

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

Switch to closed connection pybot
    [Tags]   pybot
    Open Connection  ${HOST}  alias=SUT
    Login  ${USERNAME}  ${PASSWORD}
    Execute command   ls
    close connection
    Run keyword and expect error  Non-existing index or alias 'SUT'.  switch connection   SUT

Switch to closed connection jybot
    [Tags]   jybot
    Open Connection  ${HOST}  alias=SUT
    Login  ${USERNAME}  ${PASSWORD}
    Execute command   ls
    close connection
    Run keyword and expect error  Non-existing index or alias 'SUT'.  switch connection   SUT

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

Switch Connection When Previous Connection Was Closed
    Open Connection  ${HOST}  alias=alias1
    Open Connection  ${HOST}  alias=alias2
    Switch Connection  alias1
    Close Connection
    ${old_index}=  Switch Connection  alias2
    Should Be Equal As Strings  ${old_index}  None

Switch Connection Using Index When Previous Connection Was Closed
    Open Connection  ${HOST}  con1
    Open Connection  ${HOST}  con2
    Switch Connection  1
    Close Connection
    Open Connection  ${HOST}  con1
    ${conn}=  Get Connection  1
    Should Be Equal As Integers  ${conn.index}  1
    Should Be Equal As Strings  ${conn.alias}  con2
    ${conn2}=  Get Connection  2
    Should Be Equal As Integers  ${conn2.index}  2
    Should Be Equal As Strings  ${conn2.alias}  con1
    Get Connections

Connection To Host Read From SSH Config File
   [Tags]  pybot
   Open Connection  ${TEST_HOSTNAME}

*** Keywords ***
Connection Should Be Closed
    Run Keyword And Expect Error  No open connection.  Write  pwd
