*** Settings ***
Force Tags     pybot   jybot
Resource       resources/common.robot
Test Setup     Open Connection  ${HOST}
Test Teardown  Close All Connections
Library        OperatingSystem

*** Variables ***
${LOCAL PORT}  9000
${REMOTE HOST}  google.com
${REMOTE PORT}  80
${DEFAULT SSH PORT}  22
${LOCAL SSH PORT}  2222

*** Test Cases ***
Local Tunnel Should Be Closed
    Login  ${USERNAME}  ${PASSWORD}
    Create Local SSH Tunnel  ${LOCAL PORT}  ${REMOTE HOST}  ${REMOTE PORT}
    Port Should Not Be Free  ${LOCAL PORT}
    Close All Connections
    Wait For Port To Be Closed  ${LOCAL PORT}
    Port Should Be Free     ${LOCAL PORT}

Local Tunnel With Public Key
    Login With Public Key  ${KEY USERNAME}  ${KEY}
    Create Local SSH Tunnel  ${LOCAL PORT}  ${REMOTE HOST}  ${REMOTE PORT}
    Port Should Not Be Free  ${LOCAL PORT}

Local Tunnel SSH
    Login  ${USERNAME}  ${PASSWORD}
    Create Local SSH Tunnel  ${LOCAL SSH PORT}  ${HOST}  ${DEFAULT SSH PORT}
    Port Should Not Be Free  ${LOCAL SSH PORT}
    Open Connection  ${HOST}  port=${LOCAL SSH PORT}
    Login  ${USERNAME}  ${PASSWORD}
    Execute Command   ls

Local Tunnel With Default Remote Port
    Login With Public Key  ${KEY USERNAME}  ${KEY}
    Create Local SSH Tunnel  ${LOCAL PORT}  ${REMOTE HOST}
    Port Should Not Be Free  ${LOCAL PORT}

*** Keywords ***
Port Should Not Be Free
    [Arguments]  ${port}
    ${result}  Run Keyword If  os.sep == '/'
    ...  Run  netstat -tulpn
    ...  ELSE
    ...  Run  netstat -an
    Should Contain  ${result}  :${port}

Port Should Be Free
    [Arguments]  ${port}
    ${result}  Run Keyword If  os.sep == '/'
    ...  Run  netstat -tulpn
    ...  ELSE
    ...  Run  netstat -an
    Should Not Contain  ${result}  :${port}

Wait For Port To Be Closed
    [Arguments]         ${port}
    Wait Until Keyword Succeeds  2 min  10s  Port Should Be Free  ${port}

