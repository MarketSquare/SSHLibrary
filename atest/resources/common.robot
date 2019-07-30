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

Check File Permissions
   [Arguments]  ${expected_permission}   ${remote_file}=to_put${/}ExampleText3.txt
   ${actual_permission}=  Execute Command  stat -c %a ${remote_file}
   Should Not Be Empty    ${actual_permission}    Failed to determine permissions for file:\t${remote_file}
   Should Be Equal As Integers  ${actual_permission}  ${expected_permission}  File '${remote_file}' does not have expected permissions '${expected_permission}' set:\t${actual_permission}
