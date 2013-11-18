*** Settings ***
Force Tags  pybot   jybot
Library     SSHLibrary  3 minutes 30 seconds  ${NONE}  >>       ${NONE}  ${NONE}
...                                           ${NONE}  ${NONE}  \\

*** Test Cases ***
Importing Library With Arguments
    [Setup]  Open Connections
    ${conn}=  Get Connections
    Should Be Equal As Integers  ${conn[0].timeout}  210
    Should Be Equal  ${conn[0].prompt}  >>
    Should Be Equal  ${conn[1].path_separator}  \\
    Should Be Equal As Integers  ${conn[1].timeout}  60
    Should Be Equal  ${conn[1].prompt}  >>
    Should Be Equal  ${conn[1].path_separator}  \\
    [Teardown]  Close All Connections

*** Keywords ***
Open Connections
    Open Connection  localhost
    Set Default Configuration  timeout=1 minute
    Open Connection  localhost
