*** Settings ***
Library     SSHLibrary  WITH NAME  SSH

*** Variables ***
${USERNAME}               test
${PASSWORD}               test
${HOST}                   localhost
${PROMPT}                 $
${REMOTE TEST ROOT NAME}  robot-testdir
${HOME_TEST}              /home/test
${REMOTE TEST ROOT}       ${HOME_TEST}${/}${REMOTE TEST ROOT NAME}
${CYGWIN HOME}            c:/cygwin64
${REMOTE WINDOWS TEST ROOT}  ${CYGWIN HOME}${REMOTE TEST ROOT}
${LOCAL TESTDATA}         ${CURDIR}${/}..${/}testdata

*** Keywords ***
Login As Valid User
    Open Connection  ${HOST}  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}

Remove Test Files And Close Connections
    Execute Command  rm -rf ${REMOTE TEST ROOT}
    Close All Connections
