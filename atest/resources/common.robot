*** Settings ***
Library     SSHLibrary  WITH NAME  SSH

*** Variables ***
${USERNAME}               test
${PASSWORD}               test
${HOST}                   localhost
${PROMPT}                 $
${REMOTE TEST ROOT NAME}  robot-testdir
${REMOTE HOME TEST}       /home/test
${REMOTE TEST ROOT}       ${REMOTE HOME TEST}/${REMOTE TEST ROOT NAME}
${CYGWIN HOME}            c:/cygwin64
${REMOTE WINDOWS TEST ROOT}  ${CYGWIN HOME}${REMOTE TEST ROOT}
${LOCAL TESTDATA}         ${CURDIR}${/}..${/}testdata
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY USERNAME}      testkey
${KEY}               ${KEY DIR}${/}id_rsa
${TEST_HOSTNAME}     test_hostname

*** Keywords ***
Login As Valid User
    Open Connection  ${HOST}  prompt=${PROMPT}
    Login  ${USERNAME}  ${PASSWORD}

Remove Test Files And Close Connections
    Execute Command  rm -rf ${REMOTE TEST ROOT}
    Close All Connections
