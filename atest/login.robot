*** Settings ***
Force Tags     pybot   jybot
Resource       resources/common.robot
Test Setup     Open Connection  ${HOST}
Test Teardown  Close All Connections

*** Variables ***
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY USERNAME}      testkey
${KEY}               ${KEY DIR}${/}id_rsa
${INVALID USERNAME}  invalidusername
${INVALID PASSWORD}  invalidpassword
${INVALID KEY}       ${KEY DIR}${/}id_rsa_invalid
${PASSPHRASE}        ${EMPTY}

*** Test Cases ***
Login With Valid Username And Password
    Login As Valid User

Login With Invalid Username Or Password
    [Setup]  Open Connection  ${HOST}
    Run Keyword And Expect Error  Authentication failed for user '${INVALID USERNAME}'.
    ...                           Login  ${INVALID USERNAME}  ${PASSWORD}

Login With Public Key When Valid Username And Key
    [Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
    Login With Public Key  ${KEY USERNAME}  ${KEY}

Login With Public Key When Valid Credentials
    [Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
    Login With Public Key  ${KEY USERNAME}  ${KEY}  ${PASSPHRASE}

Login With Public Key When Invalid Username
    Run Keyword And Expect Error  SSHException: not a valid OPENSSH private key file
    ...    Login With Public Key  ${INVALID USERNAME}  ${KEY}

Login With Public Key When Invalid Key
    Run Keyword And Expect Error  SSHException: not a valid OPENSSH private key file
    ...    Login With Public Key  ${KEY USERNAME}  ${INVALID KEY}  ${PASSPHRASE}

Login With Public Key When Invalid Key And Valid Password
    Run Keyword And Expect Error  SSHException: not a valid OPENSSH private key file
    ...    Login With Public Key  ${USERNAME}  ${INVALID KEY}  ${PASSWORD}

Login With Public Key When Non-Existing Key
    Run Keyword And Expect Error  Given key file 'not_existing_key' does not exist.
    ...    Login With Public Key  ${KEY USERNAME}  not_existing_key

Logging In Returns Server Output
    [Setup]  Open Connection  ${HOST}
    ${output}=  Login  ${USERNAME}  ${PASSWORD}
    Should Contain  ${output}  Last login:
    ${output}=  Read
    Should Be Equal  ${output.strip()}  ${EMPTY}

Logging In Returns Server Output If Prompt Is Set
    [Setup]  Open Connection  ${HOST}  prompt=${PROMPT}
    ${output}=  Login With Public Key  ${KEY USERNAME}  ${KEY}
    Should Contain  ${output}  Last login:
    ${output}=  Read
    Should Be Equal  ${output.strip()}  ${EMPTY}
