*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections
Library        OperatingSystem

*** Test Cases ***
Enable Logging
    [Tags]   pybot
    [Setup]  Remove File  ${OUTPUTDIR}${/}sshlog.txt
    Enable SSH Logging  ${OUTPUTDIR}${/}sshlog.txt
    Login As Valid User
    File Should Not Be Empty  ${OUTPUTDIR}${/}sshlog.txt

Log Level To None
    [Documentation]  LOG  2.2:1  NONE
    ...              LOG  2.2:2  NONE
    Set Default Configuration   loglevel=NONE
    Login As Valid User
    [Teardown]   Set Default Configuration   loglevel=INFO

Log Level To Info
    [Documentation]  LOG  1.2:1  GLOB: Logging into *
    ...              LOG  1.2:2  GLOB: *test@*
    Login As Valid User
