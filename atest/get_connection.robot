*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections
Library        OperatingSystem

*** Test Cases ***
Get Connection
    ${conn1_index} =  Open Connection  ${HOST}  alias=one
    ${conn2_index} =  Open Connection  ${HOST}
    ${conn} =  Get Connection
    Should Be Equal  ${conn.index}  ${conn2_index}
    ${conn} =  Get Connection  one
    Should Be Equal  ${conn.index}  ${conn1_index}
    ${conn} =  Get Connection  2
    Should Be Equal  ${conn.index}  ${conn2_index}

Get Connection When No Connection Is Open
    Run Keyword And Expect Error  Get Connection  1

Get Connection Index Only
    Open Connection  ${HOST}
    ${index}=  Get Connection  index=True
    Should Be Equal As Integers  ${index}  1

Get Connection Host And Timeout Only
    Open Connection  ${HOST}  timeout=3 seconds
    ${rhost}  ${timeout}=  Get Connection  host=Yes  timeout=True  port=false
    Should Be Equal  ${rhost}  ${HOST}
    Should Be Equal As Integers  ${timeout}  3

Get Connections
    Open Connection   ${HOST}   prompt=>>
    Open Connection   ${HOST}   alias=another
    ${conns} =   Get Connections
    Length Should Be   ${conns}  2
    Should Be Equal As Integers   ${conns[0].index}   1
    Should Be Equal As Integers   ${conns[1].index}   2
    Should Be Equal    ${conns[0].host}       ${HOST}
    Should Be Equal    ${conns[1].host}       ${HOST}
    Should Be Equal    ${conns[0].prompt}     >>
    Should Be Equal    ${conns[1].alias}      another
    Should Be Equal    ${conns[0].term_type}  vt100

Get Connections Returns Empty List When No Connections
    ${conns} =  Get Connections
    ${empty_list} =  Create List
    Should Be Equal  ${conns}  ${empty_list}
